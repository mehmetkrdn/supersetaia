from pathlib import Path

from ai.context_builder import build_context
from ai.metadata_service import MetadataService
from ai.nl_to_sql import question_to_sql
from backend.answer_llm import generate_llm_summary
from backend.answer_template import build_assistant_reply

from app.security.user_context import UserContext
from app.services.secure_query_pipeline import SecureQueryPipeline
from app.db.session import SessionLocal

from backend.services.sql_guardrails import prepare_llm_sql


def _build_user_context(payload) -> UserContext:
    return UserContext(
        user_id=payload.user_id,
        username=payload.username or "anonymous",
        active_company_id=payload.active_company_id,
        role_codes=payload.role_codes or [],
        permission_codes=payload.permission_codes or [],
        company_ids=payload.company_ids or [],
        country_ids=payload.country_ids or [],
        region_ids=payload.region_ids or [],
        branch_ids=payload.branch_ids or [],
        department_ids=payload.department_ids or [],
        team_ids=payload.team_ids or [],
        customer_ids=payload.customer_ids or [],
        is_superadmin=payload.is_superadmin or False,
    )


def _resolve_assistant_reply(
    user: UserContext,
    question: str,
    columns: list[str],
    rows: list[list],
    row_count: int,
    truncated: bool,
    ui_locale: str = "tr",
) -> tuple[str, list[str]]:
    try:
        answer_text, answer_bullets = generate_llm_summary(
            user=user,
            question=question,
            columns=columns,
            rows=rows,
            row_count=row_count,
            truncated=truncated,
            ui_locale=ui_locale,
        )
        if answer_text and answer_text.strip():
            return answer_text, answer_bullets or []
    except Exception as e:
        print(f"LLM summary fallback: {e}", flush=True)

    answer_text, answer_bullets = build_assistant_reply(
        user=user,
        question=question,
        columns=columns,
        row_count=row_count,
        truncated=truncated,
        ui_locale=ui_locale,
    )

    if not answer_text or not answer_text.strip():
        answer_text = f"Sorgu çalıştırıldı. {row_count} satır sonuç bulundu."
    if not answer_bullets:
        answer_bullets = [f"{row_count} satır listelendi."]

    return answer_text, answer_bullets


def _extract_selected_tables_from_context(selected_context: str) -> list[str]:
    """
    build_context(...) çıktısındaki [Seçilen tablolar] bölümünden tablo adlarını çıkarır.
    Beklenen satır formatı:
    - orders: ...
    - products
    """
    lines = (selected_context or "").splitlines()
    selected_tables: list[str] = []
    in_tables_section = False

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        if line == "[Seçilen tablolar]":
            in_tables_section = True
            continue

        if line.startswith("[") and line.endswith("]") and line != "[Seçilen tablolar]":
            # yeni bölüme geçildi
            break

        if not in_tables_section:
            continue

        if line.startswith("- "):
            item = line[2:].strip()
            table_name = item.split(":", 1)[0].strip()
            if table_name and table_name not in selected_tables:
                selected_tables.append(table_name)

    return selected_tables


def _build_selected_context(question: str) -> dict:
    """
    Gerçek metadata + context builder kullanarak selected_context üretir.
    Kişi 1 ve Kişi 2 dosyalarına dokunmadan entegrasyon için burada bir araya getirilir.
    """
    root_dir = Path(__file__).resolve().parents[2]
    metadata_path = root_dir / "ai" / "metadata" / "schema_metadata.json"

    service = MetadataService(json_path=metadata_path)
    selected_context = build_context(
        question=question,
        service=service,
        max_tables=4,
        min_tables=1,
    )
    selected_tables = _extract_selected_tables_from_context(selected_context)

    return {
        "metadata_path": str(metadata_path),
        "selected_tables": selected_tables,
        "selected_context": selected_context,
    }


def process_question(payload, ui_locale: str = "tr") -> dict:
    question = (payload.question or "").strip()
    if not question:
        raise ValueError("Soru boş olamaz.")

    user = _build_user_context(payload)

    print("USER ID:", user.user_id, flush=True)
    print("USERNAME:", user.username, flush=True)
    print("ACTIVE COMPANY:", user.active_company_id, flush=True)
    print("ROLE CODES:", user.role_codes, flush=True)
    print("QUESTION:", repr(question), flush=True)

    try:
        selection = _build_selected_context(question)
    except Exception as e:
        print(f"CONTEXT BUILDER FALLBACK: {e}", flush=True)
        selection = {
            "metadata_path": None,
            "selected_tables": [],
            "selected_context": "",
        }

    selected_tables = selection.get("selected_tables", [])
    selected_context = selection.get("selected_context", "")
    metadata_path = selection.get("metadata_path")
    prompt_type = "selected_context" if selected_context.strip() else "full_schema_fallback"

    print("METADATA PATH:", metadata_path, flush=True)
    print("SELECTED TABLES:", selected_tables, flush=True)
    print("PROMPT TYPE:", prompt_type, flush=True)
    print("SELECTED CONTEXT:", repr(selected_context), flush=True)

    model_response = question_to_sql(
        question,
        selected_context=selected_context,
    )
    print("LLM SQL:", repr(model_response), flush=True)

    raw_sql = prepare_llm_sql(model_response, requested_limit=payload.limit or 100)
    print("RAW SQL:", repr(raw_sql), flush=True)

    db = SessionLocal()
    try:
        pipeline = SecureQueryPipeline(db)
        pipeline_result = pipeline.run(
            sql=raw_sql,
            context=user,
            limit=payload.limit or 100,
        )
    finally:
        db.close()

    print("VALIDATED SQL:", repr(pipeline_result["validated_sql"]), flush=True)
    print("RLS SQL:", repr(pipeline_result["rls_sql"]), flush=True)
    print("FINAL SQL:", repr(pipeline_result["final_sql"]), flush=True)
    print("PIPELINE TABLES:", pipeline_result.get("tables", []), flush=True)
    print("RESTRICTED COLUMNS:", pipeline_result.get("restricted_columns", []), flush=True)
    print("ROW COUNT:", pipeline_result.get("row_count", 0), flush=True)

    rows_as_dicts = pipeline_result["rows"]
    columns = list(rows_as_dicts[0].keys()) if rows_as_dicts else []
    rows = [list(row.values()) for row in rows_as_dicts]

    answer_text, answer_bullets = _resolve_assistant_reply(
        user=user,
        question=question,
        columns=columns,
        rows=rows,
        row_count=len(rows),
        truncated=False,
        ui_locale=ui_locale,
    )

    return {
        "sql": pipeline_result["final_sql"],
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "total_row_count": None,
        "truncated": False,
        "error": None,
        "answer_text": answer_text or f"Sorgu çalıştırıldı. {len(rows)} satır sonuç bulundu.",
        "answer_bullets": answer_bullets or [f"{len(rows)} satır listelendi."],
    }