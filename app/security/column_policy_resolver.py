from app.security.user_context import UserContext
from app.repositories.column_security_repository import ColumnSecurityRepository


class ColumnPolicyResolver:
    def __init__(self, repo: ColumnSecurityRepository):
        self.repo = repo

    def resolve_allowed_columns(self, context: UserContext, table_name: str) -> dict:
        dataset = self.repo.get_dataset_by_table_name(table_name.lower())
        if not dataset:
            raise ValueError(f"Dataset not registered: {table_name}")

        dataset_columns = self.repo.get_dataset_columns(dataset.id)
        if not dataset_columns:
            raise ValueError(f"No dataset columns found for: {table_name}")

        all_columns = [c.column_name.lower() for c in dataset_columns]
        sensitive_columns = {c.column_name.lower() for c in dataset_columns if c.is_sensitive}

        user_rules = self.repo.get_user_rules(context.user_id, dataset.id)
        role_rules = self.repo.get_role_rules(context.user_id, context.active_company_id, dataset.id)

        user_allow = {r.column_name.lower() for r in user_rules if r.rule_type == "allow"}
        user_deny = {r.column_name.lower() for r in user_rules if r.rule_type == "deny"}

        role_allow = {r.column_name.lower() for r in role_rules if r.rule_type == "allow"}
        role_deny = {r.column_name.lower() for r in role_rules if r.rule_type == "deny"}

        # ... (üst kısımlar aynı)
        allowed = set(all_columns)

        # 1. Varsayılan olarak sensitive kolonları kapat
        if not context.is_superadmin and "admin" not in context.role_codes:
            allowed -= sensitive_columns

        # --- ÖNCE ROL KURALLARI UYGULANIR ---
        # 2. Rolün yasakladıklarını çıkar
        allowed -= role_deny
        
        # 3. Rolün izin verdiklerini ekle
        allowed |= role_allow

        # --- SONRA KULLANICI İSTİSNALARI UYGULANIR (Rolü ezer) ---
        # 4. Kullanıcıya özel yasaklanmışsa (Admin panelinden), kesinlikle çıkar
        allowed -= user_deny
        
        # 5. Kullanıcıya özel izin verilmişse (Rolünde olmasa bile), kesinlikle ekle
        allowed |= user_allow

        # Sadece gerçek kolonlar kalsın
        allowed &= set(all_columns)

        return {
            "dataset_id": dataset.id,
            "table_name": dataset.table_name.lower(),
            "all_columns": all_columns,
            "allowed_columns": sorted(allowed),
            "sensitive_columns": sorted(sensitive_columns),
        }