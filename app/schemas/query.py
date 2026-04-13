from pydantic import BaseModel

from app.security.user_context import UserContext


class SecureQueryRequest(BaseModel):
    sql: str
    context: UserContext
    limit: int = 100