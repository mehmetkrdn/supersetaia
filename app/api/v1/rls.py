from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.security.user_context import UserContext
from app.services.row_security_service import RowSecurityService

router = APIRouter()


class RLSRequest(BaseModel):
    sql: str
    context: UserContext


@router.post("/apply-rls")
def apply_rls(payload: RLSRequest, db: Session = Depends(get_db)):
    try:
        row_security_service = RowSecurityService(db)

        rewritten_sql = row_security_service.apply_rls(
            sql=payload.sql,
            context=payload.context,
        )

        return {
            "status": "ok",
            "original_sql": payload.sql,
            "rewritten_sql": rewritten_sql,
        }

    except Exception as e:
        return {
            "status": "error",
            "reason": str(e),
        }