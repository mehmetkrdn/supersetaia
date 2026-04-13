from security.roles import Role
from security.table_access import can_access_table
from security.column_access import can_access_column, TABLE_COLUMNS
from security.user_context import UserContext


def filter_query_result(user: UserContext, table_name: str, rows: list[dict]) -> list[dict]:
    """
    Query sonucunu RBAC + Column Access kurallarına göre filtreler.

    Not:
    SQL seviyesinde RLS zaten apply_sql_security ile uygulandığı için,
    burada tekrar satır bazlı filtre uygulanmaz. Aksi halde SELECT içinde
    yer almayan kolonlara göre ikinci kez eleme yapılıp doğru sonuçlar
    boş dönebilir.
    """

    # 1) tablo erişimi kontrolü
    if not can_access_table(user.role, table_name):
        return []

    # 2) kolon bazlı filtre uygulama
    filtered_rows = []
    known_columns = TABLE_COLUMNS.get(table_name, set())

    for row in rows:
        filtered_row = {}

        for column, value in row.items():
            # SQL alias / türetilmiş kolon ise olduğu gibi bırak
            if column not in known_columns:
                filtered_row[column] = value
                continue

            # gerçek tablo kolonu ise RBAC kolon kontrolü uygula
            if can_access_column(user.role, table_name, column):
                filtered_row[column] = value
            else:
                filtered_row[column] = "**REDACTED**"

        filtered_rows.append(filtered_row)

    return filtered_rows


def guard_dashboard_access(role: Role, dashboard_name: str, allowed: bool) -> dict:
    if not allowed:
        return {
            "status": "error",
            "message": f"{role.value} rolü bu dashboardu görüntüleyemez."
        }

    return {
        "status": "ok"
    }


def guard_ai_response(user: UserContext, table_name: str, rows: list[dict]) -> dict:
    filtered = filter_query_result(user, table_name, rows)

    return {
        "role": user.role.value,
        "username": user.username,
        "row_count": len(filtered),
        "data": filtered
    }