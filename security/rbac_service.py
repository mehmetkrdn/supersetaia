# security/rbac_service.py

from security.roles import Role
from security.permissions import Permission
from security.access_evaluator import (
    can_user_access_dashboard,
    can_user_access_table,
    can_user_access_column,
    can_user_do_action,
)


class RBACService:
    @staticmethod
    def check_dashboard_access(role: Role, dashboard_name: str) -> bool:
        return can_user_access_dashboard(role, dashboard_name)

    @staticmethod
    def check_table_access(role: Role, table_name: str) -> bool:
        return can_user_access_table(role, table_name)

    @staticmethod
    def check_column_access(role: Role, table_name: str, column_name: str) -> bool:
        return can_user_access_column(role, table_name, column_name)

    @staticmethod
    def check_action_access(role: Role, permission: Permission) -> bool:
        return can_user_do_action(role, permission)

    @staticmethod
    def evaluate_request(
        role: Role,
        dashboard_name: str | None = None,
        table_name: str | None = None,
        column_name: str | None = None,
        permission: Permission | None = None,
    ) -> dict:
        result = {
            "role": role.value,
            "dashboard_allowed": None,
            "table_allowed": None,
            "column_allowed": None,
            "action_allowed": None,
            "granted": True,
        }

        if dashboard_name is not None:
            result["dashboard_allowed"] = can_user_access_dashboard(role, dashboard_name)
            if not result["dashboard_allowed"]:
                result["granted"] = False

        if table_name is not None:
            result["table_allowed"] = can_user_access_table(role, table_name)
            if not result["table_allowed"]:
                result["granted"] = False

        if table_name is not None and column_name is not None:
            result["column_allowed"] = can_user_access_column(role, table_name, column_name)
            if not result["column_allowed"]:
                result["granted"] = False

        if permission is not None:
            result["action_allowed"] = can_user_do_action(role, permission)
            if not result["action_allowed"]:
                result["granted"] = False

        return result