"""
Doğal dil → SQL (Northwind, PostgreSQL).
Gemini API kullanır; şema rehberi ai/schema_prompt.md ile verilir.
API anahtarı: .env içinde GEMINI_API_KEY veya GOOGLE_API_KEY (veya ortam değişkeni).
"""

import os
import re
from pathlib import Path


def _load_dotenv() -> None:
    """Proje kökü veya ai/ klasöründeki .env dosyasını yükler."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    root = Path(__file__).resolve().parent
    load_dotenv(root / ".env")
    load_dotenv(root.parent / ".env")


def _load_schema_prompt() -> str:
    path = Path(__file__).resolve().parent / "schema_prompt.md"
    if not path.exists():
        raise FileNotFoundError(f"Şema rehberi bulunamadı: {path}")
    return path.read_text(encoding="utf-8")


def _get_api_key() -> str:
    _load_dotenv()
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise ValueError(
            "Gemini API anahtarı gerekli. Ortam değişkeni olarak GEMINI_API_KEY veya GOOGLE_API_KEY tanımlayın."
        )
    return key


def _extract_sql(text: str) -> str:
    """Yanıttan sadece SQL kodunu çıkar."""
    text = (text or "").strip()

    if not text:
        return ""

    # Markdown code fence varsa ayıkla
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if not part:
                continue

            if part.lower().startswith("sql"):
                part = part[3:].strip()

            if part.upper().startswith("SELECT") or part.upper().startswith("WITH"):
                text = part
                break

    upper_text = text.upper()

    select_pos = upper_text.find("SELECT")
    with_pos = upper_text.find("WITH")

    positions = [p for p in [select_pos, with_pos] if p != -1]
    if positions:
        start = min(positions)
        text = text[start:].strip()

    text = text.replace("```", "").strip()

    return text


def _is_read_only(sql: str) -> bool:
    cleaned = (sql or "").strip()
    cleaned = cleaned.strip(";").strip()
    cleaned = re.sub(r"^(?:\s*--.*\n)+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*/\.?\/\s", "", cleaned, flags=re.DOTALL)
    cleaned = cleaned.strip()
    sql_upper = cleaned.upper()

    forbidden = (
        "INSERT", "UPDATE", "DELETE", "DROP", "CREATE",
        "ALTER", "TRUNCATE", "MERGE", "CALL", "EXEC"
    )

    for w in forbidden:
        if re.search(rf"\b{w}\b", sql_upper):
            return False

    return sql_upper.startswith("SELECT") or sql_upper.startswith("WITH")


def _looks_complete_sql(sql: str) -> bool:
    """
    Modelin eksik / yarım / kesilmiş SQL döndürmesini yakalamak için
    basit bütünlük kontrolü yapar.
    """
    cleaned = (sql or "").strip().rstrip(";").strip()
    upper_sql = cleaned.upper()

    if not cleaned:
        return False

    if not (upper_sql.startswith("SELECT") or upper_sql.startswith("WITH")):
        return False

    if upper_sql.startswith("SELECT") and not re.search(r"\bFROM\b", upper_sql):
        return False

    if "```" in cleaned:
        return False

    return True


def _normalize_sql(sql: str) -> str:
    """
    Küçük temizlikler:
    - sonda gereksiz ;
    - fazla boşluk
    """
    cleaned = (sql or "").strip().rstrip(";").strip()
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned


def _build_common_sql_rules() -> str:
    return (
        "ZORUNLU KURALLAR:\n"
        "1. Sadece PostgreSQL uyumlu SQL üret.\n"
        "2. INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE kullanma.\n"
        "3. ORDER BY içinde kullandığın alan SELECT içinde tanımlı olmalı.\n"
        "4. Aggregate kullanıyorsan alias ver:\n"
        "   Örn: SUM(od.quantity) AS total_sales\n"
        "   ve sonra ORDER BY total_sales DESC kullan.\n"
        "5. Alias tanımlamadan ORDER BY sales, revenue, total gibi uydurma kolon isimleri kullanma.\n"
        "6. Top-N sorgularında LIMIT kullanabilirsin ama yalnızca BİR kere kullan.\n"
        "7. SQL'in sonunda gereksiz ikinci LIMIT ekleme.\n"
        "8. Geçersiz kolon veya tablo adı uydurma.\n"
        "9. Gerekli JOIN'leri açıkça yaz.\n"
        "10. Eğer soru 'en çok satan ürünler' gibi satış analizi ise mümkünse şu ilişkiyi kullan:\n"
        "    order_details od\n"
        "    JOIN orders o ON o.order_id = od.order_id\n"
        "    JOIN products p ON p.product_id = od.product_id\n"
        "11. Eğer company / scope filtreleri backend tarafından eklenecekse, sen WHERE içinde ekstra güvenlik filtresi uydurma.\n"
        "12. Eğer doğal soru toplama / sıralama içeriyorsa GROUP BY ve ORDER BY doğru sırada olsun.\n"
        "13. SQL sırası her zaman doğru olsun:\n"
        "    SELECT ...\n"
        "    FROM ...\n"
        "    JOIN ...\n"
        "    WHERE ...\n"
        "    GROUP BY ...\n"
        "    ORDER BY ...\n"
        "    LIMIT ...\n"
        "14. Çalıştırılamayacak eksik / yarım / yorumlu / açıklamalı çıktı verme.\n\n"
        "ÖRNEK DOĞRU SORGU:\n"
        "SELECT p.product_name, SUM(od.quantity) AS total_sales\n"
        "FROM order_details od\n"
        "JOIN orders o ON o.order_id = od.order_id\n"
        "JOIN products p ON p.product_id = od.product_id\n"
        "GROUP BY p.product_name\n"
        "ORDER BY total_sales DESC\n"
        "LIMIT 5\n"
    )


def _build_full_schema_system_prompt(schema: str) -> str:
    return (
        "Sen bir PostgreSQL uzmanısın. "
        "Aşağıdaki Northwind veritabanı şema rehberine göre KULLANICININ SORUSUNA "
        "YALNIZCA BİR ADET PostgreSQL SELECT sorgusu üret. "
        "Başka açıklama yazma; yanıtın sadece SQL olsun. "
        "Sadece SELECT veya WITH kullan. "
        "Yanıtın eksiksiz, tek parça, çalıştırılabilir bir PostgreSQL sorgusu olmalı.\n\n"
        f"{_build_common_sql_rules()}\n"
        "--- Şema rehberi ---\n"
        f"{schema}"
    )


def _build_selected_context_system_prompt(selected_context: str) -> str:
    return (
        "Sen bir PostgreSQL uzmanısın. "
        "Aşağıda sadece bu soru için seçilmiş veritabanı context'i veriliyor. "
        "KULLANICININ SORUSUNA YALNIZCA BİR ADET PostgreSQL SELECT sorgusu üret. "
        "Başka açıklama yazma; yanıtın sadece SQL olsun. "
        "Sadece SELECT veya WITH kullan. "
        "Yanıtın eksiksiz, tek parça, çalıştırılabilir bir PostgreSQL sorgusu olmalı.\n\n"
        f"{_build_common_sql_rules()}\n"
        "EK KISITLAR:\n"
        "15. Sadece aşağıda verilen tablo, kolon, açıklama ve join ipuçlarını kullan.\n"
        "16. Verilmeyen tablo, kolon veya ilişkiyi uydurma.\n"
        "17. Context içinde base table veya join yönü belirtilmişse buna sadık kal.\n"
        "18. Backend'in sonradan ekleyeceği scope / güvenlik filtrelerini sen WHERE içinde tekrar üretme.\n\n"
        "--- Seçilmiş context ---\n"
        f"{selected_context}"
    )


def question_to_sql(
    question: str,
    selected_context: str | None = None,
    schema_prompt: str | None = None,
) -> str:
    """
    Kullanıcı sorusunu Northwind için PostgreSQL SELECT sorgusuna çevirir.
    selected_context verilirse küçük context prompt kullanır;
    verilmezse full schema fallback ile çalışır.
    """
    import google.generativeai as genai

    api_key = _get_api_key()
    genai.configure(api_key=api_key)

    selected_context_clean = (selected_context or "").strip()

    if selected_context_clean:
        system = _build_selected_context_system_prompt(selected_context_clean)
        prompt_type = "selected_context"
    else:
        schema = schema_prompt or _load_schema_prompt()
        system = _build_full_schema_system_prompt(schema)
        prompt_type = "full_schema_fallback"

    user = (
        f"Kullanıcı sorusu: {question}\n\n"
        "Şimdi yalnızca SQL döndür."
    )

    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    model = genai.GenerativeModel(model_name)

    print("PROMPT TYPE:", prompt_type, flush=True)

    response = model.generate_content(
        f"{system}\n\n---\n\n{user}",
        generation_config=genai.types.GenerationConfig(
            temperature=0.0,
            max_output_tokens=2048,
        ),
    )

    if not response or not response.text:
        raise ValueError("Gemini yanıt üretemedi.")

    print("MODEL RAW RESPONSE:", repr(response.text), flush=True)
    sql = _extract_sql(response.text)
    sql = _normalize_sql(sql)

    print("EXTRACTED SQL:", repr(sql), flush=True)

    if not sql:
        raise ValueError("Model çıktısından SQL çıkarılamadı.")

    if not _is_read_only(sql):
        raise ValueError("Güvenlik: Sadece SELECT sorgularına izin veriliyor. Üretilen SQL reddedildi.")

    if not _looks_complete_sql(sql):
        raise ValueError("Model eksik veya tamamlanmamış SQL üretti. Lütfen tekrar deneyin.")

    return sql


def main():
    """Örnek kullanım: komut satırından bir soru verince SQL döner."""
    import sys

    if len(sys.argv) < 2:
        print('Kullanım: python nl_to_sql.py "En çok satan 5 ürün hangileri?"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    try:
        sql = question_to_sql(question)
        print(sql)
    except Exception as e:
        print(f"Hata: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()