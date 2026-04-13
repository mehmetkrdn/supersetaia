from enum import Enum


class Permission(str, Enum):
    READ_DATA = "read_data"
    RUN_QUERY = "run_query"

    CREATE_CHART = "create_chart"
    EDIT_CHART = "edit_chart"
    DELETE_CHART = "delete_chart"

    CREATE_DASHBOARD = "create_dashboard"
    EDIT_DASHBOARD = "edit_dashboard"
    PUBLISH_DASHBOARD = "publish_dashboard"
    DELETE_DASHBOARD = "delete_dashboard"

    VIEW_CUSTOMER_ANALYTICS = "view_customer_analytics"
    VIEW_EMPLOYEE_SALES = "view_employee_sales"
    VIEW_ORDER_SUMMARY = "view_order_summary"
    VIEW_PRODUCT_PERFORMANCE = "view_product_performance"
    VIEW_CATEGORY_PERFORMANCE = "view_category_performance"
    VIEW_SALES_SUMMARY = "view_sales_summary"

    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    MANAGE_RLS = "manage_rls"
    MANAGE_DATABASE = "manage_database"
    IMPORT_EXPORT = "import_export"


ALL_PERMISSIONS = [p for p in Permission]