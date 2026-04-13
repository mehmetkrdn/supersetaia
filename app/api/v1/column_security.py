from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.security.user_context import UserContext
from app.services.column_security_service import ColumnSecurityService

router = APIRouter()


class ColumnSecurityRequest(BaseModel):
    sql: str
    context: UserContext


@router.post("/apply-column-security")
def apply_column_security(payload: ColumnSecurityRequest, db: Session = Depends(get_db)):
    try:
        service = ColumnSecurityService(db)
        result = service.apply_column_security(payload.sql, payload.context)

        return {
            "status": "ok",
            **result,
        }

    except Exception as e:
        return {
            "status": "error",
            "reason": str(e),
        }