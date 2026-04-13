import re


class SQLRewriter:
    CLAUSE_PATTERN = re.compile(
        r"\b(GROUP\s+BY|ORDER\s+BY|LIMIT|OFFSET)\b",
        re.IGNORECASE,
    )

    WHERE_PATTERN = re.compile(r"\bWHERE\b", re.IGNORECASE)

    def apply_filters(self, sql: str, scope_map: dict[str, list]) -> str:
        if not scope_map:
            return sql.strip().rstrip(";")

        sql_clean = sql.strip().rstrip(";")
        predicates = self._build_predicates(scope_map)

        if not predicates:
            return sql_clean

        combined_predicate = " AND ".join(predicates)

        if self.WHERE_PATTERN.search(sql_clean):
            return self._append_to_existing_where(sql_clean, combined_predicate)

        return self._insert_new_where(sql_clean, combined_predicate)

    def _build_predicates(self, scope_map: dict[str, list]) -> list[str]:
        predicates = []

        for column_name, values in scope_map.items():
            if not values:
                continue

            formatted_values = ", ".join(self._format_value(v) for v in values)
            predicates.append(f"{column_name} IN ({formatted_values})")

        return predicates

    def _format_value(self, value):
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"

        if isinstance(value, (int, float)):
            return str(value)

        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"

    def _append_to_existing_where(self, sql: str, predicate: str) -> str:
        match = self.CLAUSE_PATTERN.search(sql)

        if match:
            where_part = sql[:match.start()].rstrip()
            tail_part = sql[match.start():].lstrip()
        else:
            where_part = sql.rstrip()
            tail_part = ""

        return f"{where_part} AND ({predicate})" + (f" {tail_part}" if tail_part else "")

    def _insert_new_where(self, sql: str, predicate: str) -> str:
        match = self.CLAUSE_PATTERN.search(sql)

        if match:
            head = sql[:match.start()].rstrip()
            tail = sql[match.start():].lstrip()
            return f"{head} WHERE ({predicate}) {tail}"

        return f"{sql} WHERE ({predicate})"