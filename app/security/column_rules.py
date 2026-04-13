COLUMN_SECURITY_RULES = {

    "orders": {
        "employee": [
            "freight"
        ],
        "customer": [
            "freight",
            "employee_id"
        ]
    },

    "products": {
        "employee": [
            "unit_price"
        ],
        "customer": [
            "unit_price",
            "supplier_id"
        ]
    },

    "employees": {
        "employee": [
            "birth_date",
            "home_phone",
            "notes"
        ],
        "customer": [
            "birth_date",
            "home_phone",
            "notes",
            "hire_date"
        ]
    }

}