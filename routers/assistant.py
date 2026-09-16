from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from assistant.copilot import ask_copilot
import models, schemas

router = APIRouter(prefix='/assistant', tags=['Assistant'])

@router.get('/query')
def get_assistant(query : schemas.AssistantQuery, db : Session = Depends(get_db)):
    result = ask_copilot(query, db)
    return {"answer" : result}