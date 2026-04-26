from fastapi import FastAPI
from dotenv import load_dotenv

from app.db.session import engine, Base
from app.routes.context import router as context_router
from app.routes.auth import router as auth_router

load_dotenv()

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ContextShift API")

app.include_router(auth_router)
app.include_router(context_router)

@app.get("/")
def root():
    return {"message": "Welcome to ContextShift API"}
