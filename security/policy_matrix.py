from security.roles import Role
from security.permissions import Permission


ROLE_PERMISSIONS = {
    Role.ADMIN: {
        Permission.READ_DATA,
        Permission.RUN_QUERY,
        Permission.CREATE_CHART,
        Permission.EDIT_CHART,
        Permission.DELETE_CHART,
        Permission.CREATE_DASHBOARD,
        Permission.EDIT_DASHBOARD,
        Permission.PUBLISH_DASHBOARD,
        Permission.DELETE_DASHBOARD,
        Permission.VIEW_CUSTOMER_ANALYTICS,
        Permission.VIEW_EMPLOYEE_SALES,
        Permission.VIEW_ORDER_SUMMARY,
        Permission.VIEW_PRODUCT_PERFORMANCE,
        Permission.VIEW_CATEGORY_PERFORMANCE,
        Permission.VIEW_SALES_SUMMARY,
        Permission.MANAGE_USERS,
        Permission.MANAGE_ROLES,
        Permission.MANAGE_RLS,
        Permission.MANAGE_DATABASE,
        Permission.IMPORT_EXPORT,
    },

    Role.MANAGER: {
        Permission.READ_DATA,
        Permission.RUN_QUERY,
        Permission.CREATE_CHART,
        Permission.EDIT_CHART,
        Permission.CREATE_DASHBOARD,
        Permission.EDIT_DASHBOARD,
        Permission.PUBLISH_DASHBOARD,
        Permission.VIEW_CUSTOMER_ANALYTICS,
        Permission.VIEW_EMPLOYEE_SALES,
        Permission.VIEW_ORDER_SUMMARY,
        Permission.VIEW_PRODUCT_PERFORMANCE,
        Permission.VIEW_CATEGORY_PERFORMANCE,
        Permission.VIEW_SALES_SUMMARY,
    },

    Role.TEAM_LEAD: {
        Permission.READ_DATA,
        Permission.RUN_QUERY,
        Permission.CREATE_CHART,
        Permission.EDIT_CHART,
        Permission.CREATE_DASHBOARD,
        Permission.VIEW_CUSTOMER_ANALYTICS,
        Permission.VIEW_EMPLOYEE_SALES,
        Permission.VIEW_ORDER_SUMMARY,
        Permission.VIEW_PRODUCT_PERFORMANCE,
        Permission.VIEW_CATEGORY_PERFORMANCE,
        Permission.VIEW_SALES_SUMMARY,
    },

    Role.EMPLOYEE: {
        Permission.READ_DATA,
        Permission.RUN_QUERY,
        Permission.VIEW_ORDER_SUMMARY,
        Permission.VIEW_PRODUCT_PERFORMANCE,
        Permission.VIEW_CATEGORY_PERFORMANCE,
        Permission.VIEW_SALES_SUMMARY,
    },

    Role.CUSTOMER: {
        Permission.RUN_QUERY,
        Permission.READ_DATA,
    },

    Role.HR: {
        Permission.RUN_QUERY,
        Permission.READ_DATA,
        Permission.VIEW_EMPLOYEE_SALES,
    },

    Role.GUEST: {
        Permission.READ_DATA,
        Permission.VIEW_PRODUCT_PERFORMANCE,
        Permission.VIEW_CATEGORY_PERFORMANCE,
        Permission.VIEW_SALES_SUMMARY,
    },
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())