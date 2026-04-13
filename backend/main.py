import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# Proje kökünü Python path'ine ekle
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from backend.schemas import AskRequest, AskResponse
from backend.services.query_service import process_question

from app.core.config import settings
from app.db.init_db import init_db

from app.api.routes import query
from app.api.v1.test import router as test_router
from app.api.v1.query import router as query_router
from app.api.v1.context import router as context_router
from app.api.v1.rls import router as rls_router
from app.api.v1.column_security import router as column_router
from app.api.v1.auth import router as auth_router
from app.api.v1.admin import router as admin_router

app = FastAPI(title=getattr(settings, "PROJECT_NAME", "Northwind Sorgu API"))


@app.on_event("startup")
def on_startup():
    init_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "AI Superset Security Gateway Running"}


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# Eski app route'ları
app.include_router(query.router, prefix="/api/v1")
app.include_router(test_router, prefix="/api/v1", tags=["health"])
app.include_router(query_router, prefix="/api/v1", tags=["query"])
app.include_router(context_router, prefix="/api/v1", tags=["context"])
app.include_router(rls_router, prefix="/api/v1", tags=["rls"])
app.include_router(column_router, prefix="/api/v1", tags=["column_security"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])


# Mevcut chatbot ask endpoint'i
@app.post("/api/ask", response_model=AskResponse)
def ask_question(payload: AskRequest, request: Request):
    question = payload.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Soru boş olamaz.")

    try:
        ui_locale = request.headers.get("x-ui-locale", "tr")
        result = process_question(payload, ui_locale=ui_locale)
        return AskResponse(**result)

    except PermissionError as e:
        return AskResponse(
            sql="",
            columns=[],
            rows=[],
            row_count=0,
            total_row_count=None,
            truncated=False,
            error=str(e),
            answer_text="",
            answer_bullets=[],
        )

    except ValueError as e:
        return AskResponse(
            sql="",
            columns=[],
            rows=[],
            row_count=0,
            total_row_count=None,
            truncated=False,
            error=str(e),
            answer_text="",
            answer_bullets=[],
        )

    except Exception as e:
        return AskResponse(
            sql="",
            columns=[],
            rows=[],
            row_count=0,
            total_row_count=None,
            truncated=False,
            error=f"Sistem hatası: {str(e)}",
            answer_text="",
            answer_bullets=[],
        )
    except PermissionError as e:
        return AskResponse(
            sql="", columns=[], rows=[], row_count=0, total_row_count=None,
            truncated=False, error=str(e),
            answer_text=f"Yetki Hatası: {str(e)}", # Değişen kısım
            answer_bullets=[],
        )

    except ValueError as e:
        return AskResponse(
            sql="", columns=[], rows=[], row_count=0, total_row_count=None,
            truncated=False, error=str(e),
            answer_text=f"Bir sorun oluştu: {str(e)}", # Değişen kısım
            answer_bullets=[],
        )

    except Exception as e:
        return AskResponse(
            sql="", columns=[], rows=[], row_count=0, total_row_count=None,
            truncated=False, error=f"Sistem hatası: {str(e)}",
            answer_text=f"Beklenmeyen bir hata oluştu: {str(e)}", # Değişen kısım
            answer_bullets=[],
        )