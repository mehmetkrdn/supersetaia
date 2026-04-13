import sqlparse
from app.security.column_rules import COLUMN_SECURITY_RULES


class ColumnGuard:

    def get_blocked_columns(self, table_name: str, role_codes: list[str]) -> list[str]:

        blocked = []

        if table_name not in COLUMN_SECURITY_RULES:
            return blocked

        rules = COLUMN_SECURITY_RULES[table_name]

        for role in role_codes:
            if role in rules:
                blocked.extend(rules[role])

        return list(set(blocked))