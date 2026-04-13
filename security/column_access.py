from security.roles import Role

TABLE_COLUMNS = {
    "categories": {
        "category_id",
        "category_name",
        "description",
        "picture",
    },
    "products": {
        "product_id",
        "product_name",
        "supplier_id",
        "category_id",
        "quantity_per_unit",
        "unit_price",
        "units_in_stock",
        "units_on_order",
        "reorder_level",
        "discontinued",
    },
    "suppliers": {
        "supplier_id",
        "company_name",
        "contact_name",
        "contact_title",
        "address",
        "city",
        "region",
        "postal_code",
        "country",
        "phone",
        "fax",
        "homepage",
    },
    "order_details": {
        "order_id",
        "product_id",
        "unit_price",
        "quantity",
        "discount",
    },
    "customers": {
        "customer_id",
        "company_name",
        "contact_name",
        "contact_title",
        "address",
        "city",
        "region",
        "postal_code",
        "country",
        "phone",
        "fax",
    },
    "customer_customer_demo": {
        "customer_id",
        "customer_type_id",
    },
    "customer_demographics": {
        "customer_type_id",
        "customer_desc",
    },
    "orders": {
        "order_id",
        "customer_id",
        "employee_id",
        "order_date",
        "required_date",
        "shipped_date",
        "ship_via",
        "freight",
        "ship_name",
        "ship_address",
        "ship_city",
        "ship_region",
        "ship_postal_code",
        "ship_country",
    },
    "shippers": {
        "shipper_id",
        "company_name",
        "phone",
    },
    "employees": {
        "employee_id",
        "last_name",
        "first_name",
        "title",
        "title_of_courtesy",
        "birth_date",
        "hire_date",
        "address",
        "city",
        "region",
        "postal_code",
        "country",
        "home_phone",
        "extension",
        "photo",
        "notes",
        "reports_to",
        "photo_path",
    },
    "employee_territories": {
        "employee_id",
        "territory_id",
    },
    "territories": {
        "territory_id",
        "territory_description",
        "region_id",
    },
    "region": {
        "region_id",
        "region_description",
    },
    "us_states": {
        "state_id",
        "state_name",
        "state_abbr",
        "state_region",
    },
}

SENSITIVE_COLUMNS = {
    "suppliers": {"address", "postal_code", "phone", "fax", "homepage"},
    "customers": {"address", "postal_code", "phone", "fax", "contact_name"},
    "orders": {"ship_address", "ship_postal_code"},
    "shippers": {"phone"},
    "employees": {
        "birth_date",
        "address",
        "postal_code",
        "home_phone",
        "photo",
        "notes",
        "photo_path",
    },
}

ROLE_COLUMN_ACCESS = {
    Role.ADMIN: {
        table_name: columns.copy()
        for table_name, columns in TABLE_COLUMNS.items()
    },

    Role.MANAGER: {
        "categories": TABLE_COLUMNS["categories"],
        "products": TABLE_COLUMNS["products"],
        "suppliers": TABLE_COLUMNS["suppliers"] - SENSITIVE_COLUMNS["suppliers"],
        "order_details": TABLE_COLUMNS["order_details"],
        "customers": TABLE_COLUMNS["customers"] - SENSITIVE_COLUMNS["customers"],
        "orders": TABLE_COLUMNS["orders"] - SENSITIVE_COLUMNS["orders"],
        "shippers": TABLE_COLUMNS["shippers"],
        "employees": TABLE_COLUMNS["employees"] - SENSITIVE_COLUMNS["employees"],
        "territories": TABLE_COLUMNS["territories"],
        "region": TABLE_COLUMNS["region"],
        "us_states": TABLE_COLUMNS["us_states"],
    },

    Role.TEAM_LEAD: {
        "categories": TABLE_COLUMNS["categories"],
        "products": TABLE_COLUMNS["products"],
        "suppliers": TABLE_COLUMNS["suppliers"] - SENSITIVE_COLUMNS["suppliers"],
        "order_details": TABLE_COLUMNS["order_details"],
        "customers": TABLE_COLUMNS["customers"] - SENSITIVE_COLUMNS["customers"],
        "orders": TABLE_COLUMNS["orders"] - SENSITIVE_COLUMNS["orders"],
        "shippers": TABLE_COLUMNS["shippers"],
        "employees": (
            TABLE_COLUMNS["employees"]
            - SENSITIVE_COLUMNS["employees"]
            - {"first_name", "last_name"}
        ),
        "territories": TABLE_COLUMNS["territories"],
        "region": TABLE_COLUMNS["region"],
        "us_states": TABLE_COLUMNS["us_states"],
    },

    Role.EMPLOYEE: {
        "categories": TABLE_COLUMNS["categories"],
        "products": TABLE_COLUMNS["products"],
        "order_details": TABLE_COLUMNS["order_details"],
        "orders": {
            "order_id",
            "order_date",
            "required_date",
            "shipped_date",
            "ship_via",
            "freight",
            "ship_city",
            "ship_region",
            "ship_country",
        },
        "shippers": {"shipper_id", "company_name"},
        "territories": TABLE_COLUMNS["territories"],
        "region": TABLE_COLUMNS["region"],
        "us_states": TABLE_COLUMNS["us_states"],
    },

    Role.CUSTOMER: {
    "categories": {"category_id", "category_name", "description"},
    "products": {
        "product_id",
        "product_name",
        "category_id",
        "quantity_per_unit",
        "unit_price",
        "discontinued",
    },
    "order_details": {
        "order_id",
        "product_id",
        "unit_price",
        "quantity",
        "discount",
    },
    "orders": {
        "order_id",
        "customer_id",  # ← bunu ekledik
        "order_date",
        "required_date",
        "shipped_date",
        "freight",
        "ship_name",
        "ship_city",
        "ship_region",
        "ship_country",
    },
    "shippers": {"company_name"},
    },

    Role.HR: {
        "employees": {
            "employee_id",
            "last_name",
            "first_name",
            "title",
            "title_of_courtesy",
            "hire_date",
            "city",
            "region",
            "country",
            "extension",
            "reports_to",
        },
        "employee_territories": TABLE_COLUMNS["employee_territories"],
        "territories": TABLE_COLUMNS["territories"],
        "region": TABLE_COLUMNS["region"],
    },

    Role.GUEST: {
        "categories": {"category_id", "category_name", "description"},
        "products": {
            "product_id",
            "product_name",
            "category_id",
            "quantity_per_unit",
            "unit_price",
            "discontinued",
        },
        "shippers": {"company_name"},
    },
}


def can_access_column(role: Role, table_name: str, column_name: str) -> bool:
    allowed_columns = ROLE_COLUMN_ACCESS.get(role, {}).get(table_name, set())
    return column_name in allowed_columns


def get_allowed_columns(role: Role, table_name: str) -> list[str]:
    allowed_columns = ROLE_COLUMN_ACCESS.get(role, {}).get(table_name, set())
    return sorted(list(allowed_columns))


def get_masked_columns(role: Role, table_name: str) -> list[str]:
    all_columns = TABLE_COLUMNS.get(table_name, set())
    allowed_columns = ROLE_COLUMN_ACCESS.get(role, {}).get(table_name, set())
    return sorted(list(all_columns - allowed_columns))