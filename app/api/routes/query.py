from fastapi import APIRouter
from app.services.query_executor import QueryExecutor

router = APIRouter()

executor = QueryExecutor()


@router.post("/run-query")
def run_query(sql: str):

    result = executor.execute_query(sql)

    return {
        "rows": result,
        "row_count": len(result)
    }