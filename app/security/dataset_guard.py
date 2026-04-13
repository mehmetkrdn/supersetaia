from app.security.table_extractor import TableExtractor


class DatasetGuard:
   

    def __init__(self):
        self.extractor = TableExtractor()

        # geçici whitelist
        # sonra bunu veritabanındaki datasets tablosundan çekeceğiz
        self.allowed_tables = {
            "orders",
            "customers",
            "products",
            "employees",
            "order_details",
            "suppliers",
            "categories",
        }

    def check_tables(self, sql: str) -> list[str]:
        tables = self.extractor.extract_tables(sql)

        if not tables:
            raise ValueError("No table found in SQL")

        blocked_tables = [table for table in tables if table not in self.allowed_tables]

        if blocked_tables:
            raise ValueError(f"Unauthorized table access: {', '.join(blocked_tables)}")

        return tables