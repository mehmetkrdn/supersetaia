import re

class TableExtractor:
    """
    Very simple table extractor for SELECT queries.
    First version:
    - FROM <table>
    - JOIN <table>
    Supports:
    - schema.table
    - table alias
    """

    FROM_JOIN_PATTERN = re.compile(
        r"\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_\.]*)",
        re.IGNORECASE,
    )

    def extract_tables(self, sql: str) -> list[str]:
        # 1. EXTRACT, SUBSTRING, TRIM gibi içinde "FROM" kelimesi geçen SQL fonksiyonlarını geçici olarak temizle
        # Böylece "EXTRACT(MONTH FROM o.order_date)" içindeki o.order_date bir tablo zannedilmeyecek!
        clean_sql = re.sub(r"\b(EXTRACT|SUBSTRING|TRIM)\s*\([^)]+\)", "", sql or "", flags=re.IGNORECASE)
        
        matches = self.FROM_JOIN_PATTERN.findall(clean_sql)
        tables = []

        for match in matches:
            # 2. Eğer "public.orders" veya "dbo.orders" gibi noktalı bir yapı gelirse, 
            # sadece tablonun asıl adını (orders) al.
            table_name = match.strip().lower().split('.')[-1]

            if table_name not in tables:
                tables.append(table_name)

        return tables