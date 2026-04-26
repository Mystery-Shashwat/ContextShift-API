from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.context import ContextModel
from app.models.user import UserModel
from app.schemas.context import ContextCreateRequest, ContextResponse, ResumeResponse
from app.services.llm_service import generate_structured_context
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/save", response_model=ContextResponse)
async def save_context(
    request: ContextCreateRequest, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Call LLM to structure context
    structured_data = await generate_structured_context(request.raw_context)
    
    def safe_str(val):
        if val is None: return None
        if isinstance(val, (dict, list)): return str(val)
        return str(val)

    def safe_list(val):
        if isinstance(val, list):
            return [str(v.get("question", v)) if isinstance(v, dict) else str(v) for v in val]
        return [] if val is None else [str(val)]

    db_context = ContextModel(
        user_id=current_user.id,
        problem=safe_str(structured_data.get("problem")),
        current_progress=safe_str(structured_data.get("current_progress")),
        next_step=safe_str(structured_data.get("next_step")),
        open_questions=safe_list(structured_data.get("open_questions")),
        notes=safe_str(structured_data.get("notes"))
    )
    
    db.add(db_context)
    db.commit()
    db.refresh(db_context)
    
    return db_context

@router.get("/resume/{context_id}", response_model=ResumeResponse)
def resume_context(
    context_id: str, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_context = db.query(ContextModel).filter(ContextModel.id == context_id, ContextModel.user_id == current_user.id).first()
    if not db_context:
        raise HTTPException(status_code=404, detail="Context not found")
        
    summary = f"Problem: {db_context.problem}. Progress: {db_context.current_progress}."
    
    return ResumeResponse(
        summary=summary,
        next_step=db_context.next_step,
        questions=db_context.open_questions
    )

@router.get("/contexts", response_model=List[ContextResponse])
def get_user_contexts(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    contexts = db.query(ContextModel).filter(ContextModel.user_id == current_user.id).all()
    return contexts
