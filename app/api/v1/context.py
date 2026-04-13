from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.context_services import ContextService

router = APIRouter()


@router.get("/context/{user_id}")
def get_user_context(user_id: int, db: Session = Depends(get_db)):
    service = ContextService(db)
    context = service.build_user_context(user_id)
    return context.model_dump()