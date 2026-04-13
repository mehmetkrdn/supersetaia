import re
from sqlalchemy.orm import Session

from app.security.user_context import UserContext
from app.security.scope_resolver import ScopeResolver
from app.security.sql_rewriter import SQLRewriter
from app.repositories.column_security_repository import ColumnSecurityRepository


class RowSecurityService:
    def __init__(self, db: Session):
        self.db = db
        self.scope_resolver = ScopeResolver()
        self.sql_rewriter = SQLRewriter()
        self.dataset_repo = ColumnSecurityRepository(db)

    def _extract_main_table_and_alias(self, sql: str) -> tuple[str, str]:
        import re
        
        # 1. Sadece "FROM tablo_adi" kısmını yakala
        match = re.search(r"\bFROM\s+([a-zA-Z0-9_\.]+)", sql, re.IGNORECASE)
        if not match:
            raise ValueError("SQL içinden ana tablo çıkarılamadı.")
        
        raw_table = match.group(1)
        table_name = raw_table.split(".")[-1].lower()
        
        # 2. FROM kısmından hemen sonrasını alıp kelimelere böl
        after_from = sql[match.end():].strip()
        
        # Alias (takma ad) olarak algılanmaması gereken SQL komutları
        sql_keywords = {
            "where", "order", "group", "limit", "offset", "join", 
            "left", "right", "inner", "cross", "having", "on",
            "union", "intersect", "except", "window"
        }
        
        table_alias = table_name  # Varsayılan olarak tablonun kendi adı
        
        if after_from:
            words = after_from.split()
            first_word = words[0].lower()
            
            if first_word == "as" and len(words) > 1:
                # "FROM employees AS e" formatındaysa
                if words[1].lower() not in sql_keywords:
                    table_alias = words[1]
            elif first_word not in sql_keywords:
                # "FROM employees e" formatındaysa (Direkt boşlukla ayrıldıysa)
                table_alias = words[0]
                
        return table_name, table_alias

    def apply_rls(self, sql: str, context: UserContext) -> str:
        # 1. Admin veya Süper Admin ise tüm verileri görür (Bypass)
        if context.is_superadmin or context.has_role("admin"):
            return sql.strip().rstrip(";")

        # 2. Tablo adını doğru şekilde yakala
        table_name, table_alias = self._extract_main_table_and_alias(sql)
        dataset = self.dataset_repo.get_dataset_by_table_name(table_name)

        # 3. Eğer tablo sistemde tanımlı değilse dokunma
        if not dataset:
            return sql.strip().rstrip(";")

        # 4. Filtreleri al
        all_filters = self.scope_resolver.resolve(context)
        filtered_scope_map = {}

        # 5. Dataset ayarlarında "contains_company_id" True ise yetki ver
        if dataset.contains_company_id and all_filters.get("company_id"):
            # Bura f"{table_name}.company_id" olarak kaldıysa hata veriyordu, ALIAS olmalı!
            filtered_scope_map[f"{table_alias}.company_id"] = all_filters["company_id"]

        if dataset.contains_country_id and all_filters.get("country_id"):
            filtered_scope_map[f"{table_alias}.country_id"] = all_filters["country_id"]

        if dataset.contains_region_id and all_filters.get("region_id"):
            filtered_scope_map[f"{table_alias}.region_id"] = all_filters["region_id"]

        if dataset.contains_branch_id and all_filters.get("branch_id"):
            filtered_scope_map[f"{table_alias}.branch_id"] = all_filters["branch_id"]

        if dataset.contains_department_id and all_filters.get("department_id"):
            filtered_scope_map[f"{table_alias}.department_id"] = all_filters["department_id"]

        if dataset.contains_team_id and all_filters.get("team_id"):
            filtered_scope_map[f"{table_alias}.team_id"] = all_filters["team_id"]

        if dataset.contains_customer_id and all_filters.get("customer_id"):
            filtered_scope_map[f"{table_alias}.customer_id"] = all_filters["customer_id"]

        # 6. SQL'e filtreleri enjekte et
        return self.sql_rewriter.apply_filters(sql, filtered_scope_map)