# security/action_policy.py

from security.roles import Role
from security.permissions import Permission
from security.policy_matrix import has_permission


def can_read_data(role: Role) -> bool:
    return has_permission(role, Permission.READ_DATA)


def can_run_query(role: Role) -> bool:
    return has_permission(role, Permission.RUN_QUERY)


def can_create_chart(role: Role) -> bool:
    return has_permission(role, Permission.CREATE_CHART)


def can_edit_chart(role: Role) -> bool:
    return has_permission(role, Permission.EDIT_CHART)


def can_delete_chart(role: Role) -> bool:
    return has_permission(role, Permission.DELETE_CHART)


def can_create_dashboard(role: Role) -> bool:
    return has_permission(role, Permission.CREATE_DASHBOARD)


def can_edit_dashboard(role: Role) -> bool:
    return has_permission(role, Permission.EDIT_DASHBOARD)


def can_publish_dashboard(role: Role) -> bool:
    return has_permission(role, Permission.PUBLISH_DASHBOARD)


def can_delete_dashboard(role: Role) -> bool:
    return has_permission(role, Permission.DELETE_DASHBOARD)


def can_view_sales_summary(role: Role) -> bool:
    return has_permission(role, Permission.VIEW_SALES_SUMMARY)


def can_view_category_performance(role: Role) -> bool:
    return has_permission(role, Permission.VIEW_CATEGORY_PERFORMANCE)


def can_view_product_performance(role: Role) -> bool:
    return has_permission(role, Permission.VIEW_PRODUCT_PERFORMANCE)


def can_view_order_summary(role: Role) -> bool:
    return has_permission(role, Permission.VIEW_ORDER_SUMMARY)


def can_view_customer_analytics(role: Role) -> bool:
    return has_permission(role, Permission.VIEW_CUSTOMER_ANALYTICS)


def can_view_employee_sales(role: Role) -> bool:
    return has_permission(role, Permission.VIEW_EMPLOYEE_SALES)


def can_manage_users(role: Role) -> bool:
    return has_permission(role, Permission.MANAGE_USERS)


def can_manage_roles(role: Role) -> bool:
    return has_permission(role, Permission.MANAGE_ROLES)


def can_manage_rls(role: Role) -> bool:
    return has_permission(role, Permission.MANAGE_RLS)


def can_manage_database(role: Role) -> bool:
    return has_permission(role, Permission.MANAGE_DATABASE)


def can_import_export(role: Role) -> bool:
    return has_permission(role, Permission.IMPORT_EXPORT)


def can_perform_action(role: Role, permission: Permission) -> bool:
    return has_permission(role, permission)