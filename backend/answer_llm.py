import json
import os
from pathlib import Path

from app.security.user_context import UserContext


_ROLE_LABELS_TR = {
    "admin": "Admin",
    "manager": "Yönetici",
    "team_leader": "Takım Lideri",
    "employee": "Çalışan",
    "customer": "Müşteri",
    "hr": "İK",
    "guest": "Misafir",
}


def _role_labels_tr(role_codes: list[str]) -> list[str]:
    labels = []
    for code in role_codes or []:
        labels.append(_ROLE_LABELS_TR.get(code, code))
    return labels


def _primary_role_label(role_codes: list[str]) -> str:
    labels = _role_labels_tr(role_codes)
    if labels:
        return labels[0]
    return "Misafir"


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    root = Path(__file__).resolve().parent
    load_dotenv(root / ".env")
    load_dotenv(root.parent / ".env")


def _get_api_key() -> str | None:
    _load_dotenv()
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def _extract_json_object(raw_text: str) -> dict:
    text = (raw_text or "").strip()
    if not text:
        raise ValueError("Boş LLM yanıtı.")

    if text.startswith(""):
        parts = text.split("")
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if part.lower().startswith("json"):
                part = part[4:].strip()
            if part.startswith("{") and part.endswith("}"):
                text = part
                break

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("LLM JSON nesnesi dönmedi.")
    return data


def generate_llm_summary(
    user: UserContext,
    question: str,
    columns: list[str],
    rows: list[list],
    row_count: int,
    truncated: bool,
    ui_locale: str = "tr",
) -> tuple[str, list[str]]:
    """
    Sonuç kümesini Gemini ile özetler.
    Başarılıysa (answer_text, answer_bullets) döner; hata durumda exception fırlatır.
    """
    import google.generativeai as genai

    api_key = _get_api_key()
    if not api_key:
        raise ValueError("Gemini API anahtarı bulunamadı.")

    genai.configure(api_key=api_key)
    model_name = os.environ.get(
        "GEMINI_SUMMARY_MODEL",
        os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
    )
    model = genai.GenerativeModel(model_name)

    max_rows = int(os.environ.get("SUMMARY_MAX_ROWS", "30"))
    sample_rows = (rows or [])[:max_rows]

    payload = {
        "question": (question or "").strip(),
        "user_id": user.user_id,
        "username": user.username,
        "primary_role": _primary_role_label(user.role_codes),
        "role_codes": user.role_codes or [],
        "role_labels_tr": _role_labels_tr(user.role_codes),
        "active_company_id": user.active_company_id,
        "company_ids": user.company_ids or [],
        "country_ids": user.country_ids or [],
        "region_ids": user.region_ids or [],
        "branch_ids": user.branch_ids or [],
        "department_ids": user.department_ids or [],
        "team_ids": user.team_ids or [],
        "customer_ids": user.customer_ids or [],
        "is_superadmin": bool(user.is_superadmin),
        "columns": columns or [],
        "row_count": int(row_count),
        "truncated": bool(truncated),
        "sample_rows": sample_rows,
        "sample_row_count": len(sample_rows),
    }

    locale = (ui_locale or "tr").lower().split("-")[0]
    if locale not in {"tr", "en", "fr", "ar"}:
        locale = "tr"

    lang_name = {
        "tr": "Türkçe",
        "en": "English",
        "fr": "Français",
        "ar": "العربية",
    }[locale]

    locale_instruction = {
        "tr": "Metin Türkçe olmalı.",
        "en": "The text must be in English.",
        "fr": "Le texte doit être en français.",
        "ar": "يجب أن يكون النص باللغة العربية.",
    }[locale]

    system_prompt = (
        "Sen veri analisti asistanısın. Sana yalnızca rol filtresi uygulanmış güvenli sorgu sonucu verilecek. "
        f"YALNIZCA verilen veriye dayanarak {lang_name} özet üret. Kesinlikle yeni veri uydurma. "
        "Görünmeyen kolon/satırlardan bahsetme. SQL yazma. Uzun anlatım yapma.\n\n"
        "Sadece geçerli JSON döndür ve başka metin ekleme. Şema:\n"
        "{\n"
        '  "answer_text": "Kısa özet paragrafı (2-4 cümle)",\n'
        '  "answer_bullets": ["Madde 1", "Madde 2", "Madde 3"]\n'
        "}\n"
        "Kurallar:\n"
        "- answer_bullets 2-4 madde olmalı.\n"
        "- row_count=0 ise veri bulunamadığını net söyle.\n"
        "- truncated=true ise sonuçların limit nedeniyle kısaltılabileceğini belirt.\n"
        f"- {locale_instruction}"
    )

    response = model.generate_content(
        f"{system_prompt}\n\nVERI:\n{json.dumps(payload, ensure_ascii=False)}",
        generation_config=genai.types.GenerationConfig(
            temperature=0.2,
            max_output_tokens=600,
        ),
    )

    if not response or not response.text:
        raise ValueError("Gemini summary yanıt üretemedi.")

    data = _extract_json_object(response.text)
    answer_text = str(data.get("answer_text", "")).strip()
    bullets_raw = data.get("answer_bullets", [])
    bullets = [str(item).strip() for item in bullets_raw if str(item).strip()]

    if not answer_text:
        raise ValueError("Gemini summary boş answer_text döndü.")
    if len(bullets) == 0:
        raise ValueError("Gemini summary madde döndüremedi.")

    return answer_text, bullets[:4]