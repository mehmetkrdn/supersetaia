from app.security.user_context import UserContext


class ScopeResolver:
    """
    Converts UserContext into SQL filter definitions.
    """

    def resolve(self, context: UserContext) -> dict[str, list[int]]:
        # 1. SÜPER ADMIN KONTROLÜ
        # Eğer kullanıcı superadmin ise hiçbir kısıtlama (scope) uygulamıyoruz.
        # Boş dict {} döndüğünde SQLRewriter sorguyu değiştirmeden bırakacak.
        if context.is_superadmin:
            return {}

        filters: dict[str, list[int]] = {}

        # 2. ŞİRKET (COMPANY) BAZLI KESİN KISITLAMA
        # Normal kullanıcıysa kesinlikle company_id filtresine tabi tutulmalı.
        # Eğer kullanıcının atandığı bir şirket yoksa, tüm verileri görmesini engellemek için
        # geçersiz bir ID olan [-1] atıyoruz (Güvenlik önlemi).
        filters["company_id"] = context.company_ids if context.company_ids else [-1]

        # Diğer isteğe bağlı bölgesel/departman kısıtlamaları
        if context.country_ids:
            filters["country_id"] = context.country_ids

        if context.region_ids:
            filters["region_id"] = context.region_ids

        if context.branch_ids:
            filters["branch_id"] = context.branch_ids

        if context.department_ids:
            filters["department_id"] = context.department_ids

        if context.team_ids:
            filters["team_id"] = context.team_ids

        if context.customer_ids:
            filters["customer_id"] = context.customer_ids

        return filters