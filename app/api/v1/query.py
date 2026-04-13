from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.security.sql_quard import SQLGuard
from app.schemas.query import SecureQueryRequest
from app.services.secure_query_pipeline import SecureQueryPipeline

router = APIRouter()
guard = SQLGuard()


@router.post("/validate-sql")
def validate_sql(sql: str):
    try:
        result = guard.check_sql(sql)
        return {
            "status": "valid",
            "sql": result["sql"],
            "tables": result["tables"],
        }
    except Exception as e:
        return {
            "status": "blocked",
            "reason": str(e),
        }


@router.post("/secure-run-query")
def secure_run_query(payload: SecureQueryRequest, db: Session = Depends(get_db)):
    try:
        pipeline = SecureQueryPipeline(db)
        result = pipeline.run(
            sql=payload.sql,
            context=payload.context,
            limit=payload.limit,
        )

        return {
            "status": "ok",
            **result,
        }
    except Exception as e:
        return {
            "status": "error",
            "reason": str(e),
        }