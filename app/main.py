from fastapi import FastAPI
from app.api.v1.column_security import router as column_router
from app.core.config import settings
from app.db.init_db import init_db
from app.api.v1.test import router as test_router
from app.api.v1.query import router as query_router
from app.api.v1.context import router as context_router
from app.api.v1.rls import router as rls_router
app = FastAPI(title=settings.PROJECT_NAME)
from app.api.routes import query
from app.api.v1.auth import router as auth_roter
from app.api.v1.admin import router as admin_router

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(query.router, prefix="/api/v1")
app.include_router(test_router, prefix="/api/v1", tags=["health"])
app.include_router(query_router, prefix="/api/v1", tags=["query"])
app.include_router(context_router, prefix="/api/v1", tags=["context"])
app.include_router(rls_router, prefix="/api/v1",tags=["rls"])
app.include_router(column_router, prefix="/api/v1", tags=["column_security"])
app.include_router(auth_roter, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
@app.get("/")
def root():
    return {"message": "AI Superset Security Gateway Running"}