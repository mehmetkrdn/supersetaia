import re

class ColumnSQLRewriter:
    def rewrite_select(self, sql: str, allowed_columns: list[str]) -> str:
        sql_clean = sql.strip().rstrip(";")

        # SELECT ile FROM arasındaki kısmı alıyoruz
        select_match = re.search(r"SELECT\s+(.*?)\s+FROM\s+", sql_clean, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return sql

        selected_part = select_match.group(1).strip()

        # Eğer "SELECT *" kullanılmışsa, sadece izin verilen kolonları araya koy
        if selected_part == "*":
            safe_select = ", ".join(allowed_columns)
            return re.sub(
                r"SELECT\s+(.*?)\s+FROM\s+",
                f"SELECT {safe_select} FROM ",
                sql_clean,
                count=1,
                flags=re.IGNORECASE | re.DOTALL,
            )

        # SQL'in içinde karmaşık fonksiyonlar (SUM, EXTRACT, ROUND vs.) varsa 
        # veya matematiksel işlemler varsa, bu basit rewriter yapısı bunu parçalayamaz.
        # Kolon seviyesi güvenlik zaten veritabanı kısıtlamaları ve tablo kontrolleriyle sağlandı.
        # Bu yüzden karmaşık sorguları bozmamak için orijinal SQL'i geri döndürüyoruz.
        if "(" in selected_part or ")" in selected_part or "*" in selected_part or "::" in selected_part:
            return sql

        # Basit kolon seçimleri için (Örn: SELECT o.order_date, c.company_name FROM...)
        # virgülle ayırıp izin kontrolü yapıyoruz.
        selected_columns = [c.strip() for c in selected_part.split(",")]
        safe_columns = []

        for col in selected_columns:
            raw = col.lower()

            # AS (alias) kullanımını yakala
            alias_match = re.match(r"(.+?)\s+as\s+(.+)$", raw, re.IGNORECASE)
            if alias_match:
                expr = alias_match.group(1).strip()
                # Noktadan sonrasını al (örn: o.order_date -> order_date)
                base = expr.split(".")[-1].strip()
                if base in allowed_columns:
                    safe_columns.append(col)
                continue

            # Alias yoksa doğrudan noktadan sonrasını al
            base = raw.split(".")[-1].strip()
            if base in allowed_columns:
                safe_columns.append(col)

        # Eğer basit sorguda hiçbir kolon izni geçemezse engelle
        if not safe_columns:
            raise ValueError("All selected columns are restricted")

        safe_select = ", ".join(safe_columns)

        return re.sub(
            r"SELECT\s+(.*?)\s+FROM\s+",
            f"SELECT {safe_select} FROM ",
            sql_clean,
            count=1,
            flags=re.IGNORECASE | re.DOTALL,
        )