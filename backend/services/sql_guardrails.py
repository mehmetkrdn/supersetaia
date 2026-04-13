import re


FORBIDDEN_SQL_WORDS = (
    "INSERT", "UPDATE", "DELETE", "DROP", "CREATE",
    "ALTER", "TRUNCATE", "MERGE", "CALL", "EXEC"
)


def extract_sql(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""

    # HATA BURADAYDI: "" yerine "```" olmalı
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
        text = text[min(positions):].strip()

    # HATA BURADAYDI: "" yerine "```" olmalı
    text = text.replace("```", "").strip()
    return text


def normalize_sql(sql: str) -> str:
    sql = (sql or "").strip()
    # HATA BURADAYDI: "" yerine "```" olmalı
    sql = sql.replace("```", "").strip()
    sql = sql.rstrip(";").strip()
    sql = re.sub(r"[ \t]+", " ", sql)
    return sql


def is_read_only(sql: str) -> bool:
    cleaned = normalize_sql(sql)
    if not cleaned:
        return False

    upper_sql = cleaned.upper()

    for word in FORBIDDEN_SQL_WORDS:
        if re.search(rf"\b{word}\b", upper_sql):
            return False

    return upper_sql.startswith("SELECT") or upper_sql.startswith("WITH")


def looks_complete_sql(sql: str) -> bool:
    cleaned = normalize_sql(sql)
    upper_sql = cleaned.upper()

    if not cleaned:
        return False

    if not (upper_sql.startswith("SELECT") or upper_sql.startswith("WITH")):
        return False

    if upper_sql.startswith("SELECT") and "FROM" not in upper_sql:
        return False

    if "```" in cleaned:
        return False

    return True


def ensure_single_statement(sql: str) -> str:
    cleaned = normalize_sql(sql)

    if ";" in cleaned:
        raise ValueError("Birden fazla SQL statement desteklenmiyor.")

    return cleaned


def split_select_items(select_part: str) -> list[str]:
    items = []
    current = []
    depth = 0

    for ch in select_part:
        if ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth = max(0, depth - 1)
            current.append(ch)
        elif ch == "," and depth == 0:
            item = "".join(current).strip()
            if item:
                items.append(item)
            current = []
        else:
            current.append(ch)

    last = "".join(current).strip()
    if last:
        items.append(last)

    return items


def fix_order_by_alias(sql: str) -> str:
    """
    SELECT içindeki alias'ı bulur ve ORDER BY alias kullanımını gerçek expression ile değiştirir.
    """
    sql_clean = normalize_sql(sql)

    match = re.search(r"SELECT\s+(.*?)\s+FROM\s", sql_clean, re.IGNORECASE | re.DOTALL)
    if not match:
        return sql_clean

    select_part = match.group(1)
    select_items = split_select_items(select_part)

    alias_map = {}

    for item in select_items:
        alias_match = re.search(
            r"(.+?)\s+AS\s+([a-zA-Z_][a-zA-Z0-9_]*)$",
            item,
            re.IGNORECASE | re.DOTALL,
        )
        if alias_match:
            expr = alias_match.group(1).strip()
            alias = alias_match.group(2).strip()
            alias_map[alias.lower()] = expr

    if not alias_map:
        return sql_clean

    def repl(match_obj):
        alias = match_obj.group(1)
        direction = match_obj.group(2) or ""
        expr = alias_map.get(alias.lower())
        if not expr:
            return match_obj.group(0)
        return f"ORDER BY {expr}{direction}"

    return re.sub(
        r"ORDER\s+BY\s+([a-zA-Z_][a-zA-Z0-9_]*)(\s+ASC|\s+DESC)?",
        repl,
        sql_clean,
        flags=re.IGNORECASE,
    )


def get_existing_limit(sql: str) -> int | None:
    match = re.search(r"\bLIMIT\s+(\d+)\b", sql, re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1))


def enforce_limit(sql: str, requested_limit: int | None, default_limit: int = 100) -> str:
    """
    LIMIT yoksa ekler.
    LIMIT varsa tekrar eklemez.
    requested_limit verilmişse mevcut LIMIT ile çakıştırır, küçük olanı seçer.
    """
    sql_clean = normalize_sql(sql)

    existing_limit = get_existing_limit(sql_clean)

    if requested_limit is None:
        requested_limit = default_limit

    if requested_limit == 0:
        return sql_clean

    if existing_limit is None:
        return f"{sql_clean} LIMIT {requested_limit}"

    final_limit = min(existing_limit, requested_limit)
    return re.sub(
        r"\bLIMIT\s+\d+\b",
        f"LIMIT {final_limit}",
        sql_clean,
        flags=re.IGNORECASE,
    )


def prepare_llm_sql(raw_text: str, requested_limit: int | None = 100) -> str:
    sql = extract_sql(raw_text)
    sql = normalize_sql(sql)

    if not sql:
        raise ValueError("Model çıktısından SQL çıkarılamadı.")

    if not is_read_only(sql):
        raise ValueError("Güvenlik: Sadece SELECT sorgularına izin veriliyor. Üretilen SQL reddedildi.")

    if not looks_complete_sql(sql):
        raise ValueError("Model eksik veya tamamlanmamış SQL üretti.")

    sql = ensure_single_statement(sql)
    sql = fix_order_by_alias(sql)
    sql = enforce_limit(sql, requested_limit=requested_limit, default_limit=100)

    return sql


