from security.roles import Role
from security.permissions import Permission
from security.policy_matrix import has_permission
from security.table_access import can_access_table, get_allowed_tables
from security.column_access import can_access_column, get_allowed_columns
from security.dashboard_access import can_access_dashboard


def can_user_do_action(role: Role, permission: Permission) -> bool:
    return has_permission(role, permission)


def can_user_access_table(role: Role, table_name: str) -> bool:
    return can_access_table(role, table_name)


def can_user_access_column(role: Role, table_name: str, column_name: str) -> bool:
    return can_access_column(role, table_name, column_name)


def can_user_access_dashboard(role: Role, dashboard_name: str) -> bool:
    return can_access_dashboard(role, dashboard_name)


def get_user_access_summary(role: Role) -> dict:
    return {
        "role": role.value,
        "allowed_tables": get_allowed_tables(role),
    }


def evaluate_full_access(
    role: Role,
    permission: Permission | None = None,
    table_name: str | None = None,
    column_name: str | None = None,
    dashboard_name: str | None = None,
) -> dict:
    result = {
        "role": role.value,
        "permission_allowed": None,
        "table_allowed": None,
        "column_allowed": None,
        "dashboard_allowed": None,
        "granted": True,
    }

    if permission is not None:
        result["permission_allowed"] = has_permission(role, permission)
        if not result["permission_allowed"]:
            result["granted"] = False

    if table_name is not None:
        result["table_allowed"] = can_access_table(role, table_name)
        if not result["table_allowed"]:
            result["granted"] = False

    if table_name is not None and column_name is not None:
        result["column_allowed"] = can_access_column(role, table_name, column_name)
        if not result["column_allowed"]:
            result["granted"] = False

    if dashboard_name is not None:
        result["dashboard_allowed"] = can_access_dashboard(role, dashboard_name)
        if not result["dashboard_allowed"]:
            result["granted"] = False

    return result