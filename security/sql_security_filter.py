import re
from security.user_context import UserContext
from security.rls_policy import get_rls_filters
from security.roles import Role


def _normalize_sql(sql: str) -> str:
    return sql.strip().rstrip(";").strip()


def _extract_table_alias_pairs(sql: str) -> list[tuple[str, str | None]]:
    """
    FROM / JOIN içindeki tablo ve alias çiftlerini çıkarır.
    """
    pattern = r"\b(?:FROM|JOIN)\s+([a-zA-Z0-9_]+)(?:\s+(?:AS\s+)?([a-zA-Z0-9_]+))?"
    matches = re.findall(pattern, sql, re.IGNORECASE)

    cleaned = []
    for table_name, alias in matches:
        if alias and alias.upper() in {"WHERE", "JOIN", "GROUP", "ORDER", "LIMIT", "HAVING", "ON"}:
            alias = None
        cleaned.append((table_name, alias))

    return cleaned


def _qualify_column(column: str, alias: str | None) -> str:
    if alias:
        return f"{alias}.{column}"
    return column


def _build_conditions_for_table(user: UserContext, table_name: str, alias: str | None) -> list[str]:
    policy = get_rls_filters(user, table_name)
    filters = policy.get("filters", [])

    allowed_columns_by_table = {
        "orders": {"customer_id", "ship_country", "ship_region"},
        "customers": {"customer_id", "country", "region"},
        "suppliers": {"country", "region"},
        "employees": {"country", "region"},
        "territories": {"territory_description"},
        "employee_territories": set(),
        "order_details": set(),
    }

    allowed_columns = allowed_columns_by_table.get(table_name, None)

    conditions = []

    for rule in filters:
        column = rule["column"]
        operator = rule["operator"]
        value = rule["value"]

        if allowed_columns is not None and column not in allowed_columns:
            continue

        qualified_column = _qualify_column(column, alias)

        if operator == "=":
            conditions.append(f"{qualified_column} = '{value}'")
        elif operator == "contains":
            conditions.append(f"{qualified_column} LIKE '%{value}%'")

    return conditions


def _remove_conflicting_scope_filters(sql: str, table_alias_pairs: list[tuple[str, str | None]]) -> str:
    """
    AI'ın yazdığı country/region filtrelerini temizler.
    Böylece kullanıcının scope filtresi baskın olur.
    """
    removable_columns = {
        "country",
        "region",
        "ship_country",
        "ship_region",
    }

    aliases = [alias for _, alias in table_alias_pairs if alias]
    columns_to_clean = set(removable_columns)

    for alias in aliases:
        for col in removable_columns:
            columns_to_clean.add(f"{alias}.{col}")

    for col in sorted(columns_to_clean, key=len, reverse=True):
        sql = re.sub(
            rf"(?i)\bAND\s+{re.escape(col)}\s*=\s*'[^']*'",
            "",
            sql,
        )
        sql = re.sub(
            rf"(?i)\bWHERE\s+{re.escape(col)}\s*=\s*'[^']*'\s+AND\s+",
            "WHERE ",
            sql,
        )
        sql = re.sub(
            rf"(?i)\bWHERE\s+{re.escape(col)}\s*=\s*'[^']*'",
            "",
            sql,
        )

    sql = re.sub(r"\s+", " ", sql).strip()
    sql = re.sub(r"(?i)\bWHERE\s+(ORDER BY|GROUP BY|HAVING|LIMIT)\b", r"\1", sql)
    sql = re.sub(r"(?i)\bWHERE\s*$", "", sql).strip()

    return sql


def apply_sql_security(user: UserContext, sql: str) -> str:
    """
    Join'li sorgular dahil tüm ilgili tablolara RLS filtresi ekler.
    Admin ve Manager için scope filtresi uygulanmaz.
    """
    sql = _normalize_sql(sql)

    # Admin ve Manager tamamen serbest
    if user.role in {Role.ADMIN, Role.MANAGER}:
        return sql

    table_alias_pairs = _extract_table_alias_pairs(sql)
    if not table_alias_pairs:
        return sql

    # AI'ın country/region scope filtrelerini sil
    sql = _remove_conflicting_scope_filters(sql, table_alias_pairs)

    # Kullanıcının gerçek scope filtrelerini topla
    all_conditions = []

    for table_name, alias in table_alias_pairs:
        table_conditions = _build_conditions_for_table(user, table_name, alias)
        all_conditions.extend(table_conditions)

    if not all_conditions:
        return sql

    where_clause = " AND ".join(all_conditions)

    # SQL'de zaten WHERE varsa başına scope filtresini koy
    if re.search(r"\bWHERE\b", sql, re.IGNORECASE):
        return re.sub(
            r"\bWHERE\b",
            f"WHERE {where_clause} AND ",
            sql,
            count=1,
            flags=re.IGNORECASE,
        )

    # ORDER BY / GROUP BY / HAVING / LIMIT öncesine WHERE ekle
    tail_pattern = r"\b(ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT)\b"
    match = re.search(tail_pattern, sql, re.IGNORECASE)

    if match:
        insert_at = match.start()
        head = sql[:insert_at].rstrip()
        tail = sql[insert_at:].lstrip()
        return f"{head} WHERE {where_clause} {tail}"

    return f"{sql} WHERE {where_clause}"