from security.roles import Role

CATEGORIES = "categories"
PRODUCTS = "products"
SUPPLIERS = "suppliers"
ORDER_DETAILS = "order_details"
CUSTOMERS = "customers"
CUSTOMER_CUSTOMER_DEMO = "customer_customer_demo"
CUSTOMER_DEMOGRAPHICS = "customer_demographics"
ORDERS = "orders"
SHIPPERS = "shippers"
EMPLOYEES = "employees"
EMPLOYEE_TERRITORIES = "employee_territories"
TERRITORIES = "territories"
REGION = "region"
US_STATES = "us_states"


ROLE_TABLE_ACCESS = {
    Role.ADMIN: {
        CATEGORIES,
        PRODUCTS,
        SUPPLIERS,
        ORDER_DETAILS,
        CUSTOMERS,
        CUSTOMER_CUSTOMER_DEMO,
        CUSTOMER_DEMOGRAPHICS,
        ORDERS,
        SHIPPERS,
        EMPLOYEES,
        EMPLOYEE_TERRITORIES,
        TERRITORIES,
        REGION,
        US_STATES,
    },

    Role.MANAGER: {
        CATEGORIES,
        PRODUCTS,
        SUPPLIERS,
        ORDER_DETAILS,
        CUSTOMERS,
        ORDERS,
        SHIPPERS,
        EMPLOYEES,
        TERRITORIES,
        REGION,
        US_STATES,
    },

    Role.TEAM_LEAD: {
        CATEGORIES,
        PRODUCTS,
        SUPPLIERS,
        ORDER_DETAILS,
        CUSTOMERS,
        ORDERS,
        SHIPPERS,
        EMPLOYEES,
        TERRITORIES,
        REGION,
        US_STATES,
    },

    Role.EMPLOYEE: {
        CATEGORIES,
        PRODUCTS,
        ORDER_DETAILS,
        ORDERS,
        SHIPPERS,
        TERRITORIES,
        REGION,
        US_STATES,
    },

    Role.CUSTOMER: {
        CATEGORIES,
        PRODUCTS,
        ORDER_DETAILS,
        ORDERS,
        SHIPPERS,
    },

    Role.HR: {
        EMPLOYEES,
        EMPLOYEE_TERRITORIES,
        TERRITORIES,
        REGION,
    },

    Role.GUEST: {
        CATEGORIES,
        PRODUCTS,
        SHIPPERS,
    },
}


def can_access_table(role: Role, table_name: str) -> bool:
    allowed_tables = ROLE_TABLE_ACCESS.get(role, set())
    return table_name in allowed_tables


def get_allowed_tables(role: Role) -> list[str]:
    return sorted(list(ROLE_TABLE_ACCESS.get(role, set())))