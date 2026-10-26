# routers/assistant.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from assistant.copilot import ask_copilot
import schemas

router = APIRouter(prefix='/assistant', tags=['Assistant'])


@router.post('/query')
def query_assistant(query: schemas.AssistantQuery, db: Session = Depends(get_db)):
    return {"answer": ask_copilot(query.question, db)}