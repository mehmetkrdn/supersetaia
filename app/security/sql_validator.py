import sqlparse


class SQLValidator:

    BLOCKED_KEYWORDS = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "GRANT",
        "REVOKE",
    ]

    ALLOWED_START = ["SELECT", "WITH"]

    def validate(self, sql: str) -> None:
        """
        Raises ValueError if SQL is not safe
        """

        if not sql:
            raise ValueError("Empty SQL")

        sql = sql.strip()

        parsed = sqlparse.parse(sql)

        if not parsed:
            raise ValueError("Invalid SQL")

        first_token = parsed[0].tokens[0].value.upper()

        if first_token not in self.ALLOWED_START:
            raise ValueError("Only SELECT queries are allowed")

        upper_sql = sql.upper()

        for keyword in self.BLOCKED_KEYWORDS:
            if keyword in upper_sql:
                raise ValueError(f"Blocked SQL keyword detected: {keyword}")