from security.user_context import UserContext
from security.response_guard import guard_ai_response
from security.dashboard_access import can_access_dashboard
from security.action_policy import can_perform_action
from security.permissions import Permission


class SecurityGateway:

    @staticmethod
    def secure_query_result(user: UserContext, table_name: str, rows: list[dict]) -> dict:
        """
        SQL sonucunu RBAC + RLS + Column Access kurallarına göre güvenli hale getirir.
        """
        return guard_ai_response(user, table_name, rows)

    @staticmethod
    def check_dashboard(user: UserContext, dashboard_name: str) -> bool:
        """
        Kullanıcının dashboard erişimini kontrol eder.
        """
        return can_access_dashboard(user.role, dashboard_name)

    @staticmethod
    def check_action(user: UserContext, permission: Permission) -> bool:
        """
        Kullanıcının belirli bir aksiyonu yapma yetkisi olup olmadığını kontrol eder.
        """
        return can_perform_action(user.role, permission)

    @staticmethod
    def evaluate_security(user: UserContext, table_name: str, rows: list[dict]) -> dict:
        """
        Tüm güvenlik katmanlarını çalıştırarak güvenli sonucu döner.
        """
        return SecurityGateway.secure_query_result(user, table_name, rows)
