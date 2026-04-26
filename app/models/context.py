import uuid
from sqlalchemy import Column, String, JSON, ForeignKey
from app.db.session import Base

class ContextModel(Base):
    __tablename__ = "contexts"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    problem = Column(String)
    current_progress = Column(String)
    next_step = Column(String)
    open_questions = Column(JSON)
    notes = Column(String)
