from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.context import ContextModel
from app.schemas.context import ContextCreateRequest, ContextResponse, ResumeResponse
from app.services.llm_service import generate_structured_context

router = APIRouter()

@router.post("/save", response_model=ContextResponse)
async def save_context(request: ContextCreateRequest, db: Session = Depends(get_db)):
    # Call LLM to structure context
    structured_data = await generate_structured_context(request.raw_context)
    
    db_context = ContextModel(
        user_id=request.user_id,
        problem=structured_data.get("problem"),
        current_progress=structured_data.get("current_progress"),
        next_step=structured_data.get("next_step"),
        open_questions=structured_data.get("open_questions", []),
        notes=structured_data.get("notes")
    )
    
    db.add(db_context)
    db.commit()
    db.refresh(db_context)
    
    return db_context

@router.get("/resume/{context_id}", response_model=ResumeResponse)
def resume_context(context_id: str, db: Session = Depends(get_db)):
    db_context = db.query(ContextModel).filter(ContextModel.id == context_id).first()
    if not db_context:
        raise HTTPException(status_code=404, detail="Context not found")
        
    summary = f"Problem: {db_context.problem}. Progress: {db_context.current_progress}."
    
    return ResumeResponse(
        summary=summary,
        next_step=db_context.next_step,
        questions=db_context.open_questions
    )

@router.get("/contexts/{user_id}", response_model=List[ContextResponse])
def get_user_contexts(user_id: str, db: Session = Depends(get_db)):
    contexts = db.query(ContextModel).filter(ContextModel.user_id == user_id).all()
    return contexts
