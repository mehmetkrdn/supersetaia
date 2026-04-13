# security/rls_policy.py

from security.roles import Role
from security.user_context import UserContext


def get_rls_filters(user: UserContext, table_name: str) -> dict:
    """
    Kullanıcının rolüne ve context bilgisine göre tablo bazlı satır filtresi döner.
    Şimdilik SQL değil, policy dict dönüyoruz.
    """

    role = user.role

    # Admin her şeyi görebilir
    if role == Role.ADMIN:
        return {
            "table": table_name,
            "filters": [],
            "restricted": False,
        }

    # Manager: kendi region / country alanı
    if role == Role.MANAGER:
        filters = []

        if user.region and table_name in {"orders", "customers", "suppliers", "employees"}:
            if table_name == "orders":
                filters.append({"column": "ship_region", "operator": "=", "value": user.region})
            elif table_name in {"customers", "suppliers", "employees"}:
                filters.append({"column": "region", "operator": "=", "value": user.region})

        if user.country and table_name in {"orders", "customers", "suppliers", "employees"}:
            if table_name == "orders":
                filters.append({"column": "ship_country", "operator": "=", "value": user.country})
            elif table_name in {"customers", "suppliers", "employees"}:
                filters.append({"column": "country", "operator": "=", "value": user.country})

        return {
            "table": table_name,
            "filters": filters,
            "restricted": len(filters) > 0,
        }

    # Team lead: manager gibi ama biraz daha dar kapsam
    if role == Role.TEAM_LEAD:
        filters = []

        if user.region and table_name in {"orders", "customers", "employees"}:
            if table_name == "orders":
                filters.append({"column": "ship_region", "operator": "=", "value": user.region})
            else:
                filters.append({"column": "region", "operator": "=", "value": user.region})

        if user.country and table_name in {"orders", "customers", "employees"}:
            if table_name == "orders":
                filters.append({"column": "ship_country", "operator": "=", "value": user.country})
            else:
                filters.append({"column": "country", "operator": "=", "value": user.country})

        return {
            "table": table_name,
            "filters": filters,
            "restricted": len(filters) > 0,
        }

    # Employee: kendi ülke/bölge scope'u
    if role == Role.EMPLOYEE:
        filters = []

        if user.country and table_name in {"orders", "customers", "employees"}:
            if table_name == "orders":
                filters.append({"column": "ship_country", "operator": "=", "value": user.country})
            else:
                filters.append({"column": "country", "operator": "=", "value": user.country})

        if user.region and table_name in {"orders", "customers", "employees", "territories"}:
            if table_name == "orders":
                filters.append({"column": "ship_region", "operator": "=", "value": user.region})
            elif table_name in {"customers", "employees"}:
                filters.append({"column": "region", "operator": "=", "value": user.region})
            elif table_name == "territories":
                filters.append({"column": "territory_description", "operator": "contains", "value": user.region})

        return {
            "table": table_name,
            "filters": filters,
            "restricted": len(filters) > 0,
        }

    # Customer: sadece kendi kayıtları
    if role == Role.CUSTOMER:
        filters = []

        if table_name == "orders":
            filters.append({"column": "customer_id", "operator": "=", "value": user.username})
        elif table_name == "customers":
            filters.append({"column": "customer_id", "operator": "=", "value": user.username})

        return {
            "table": table_name,
            "filters": filters,
            "restricted": len(filters) > 0,
        }

    # HR: sadece employee tarafında country/region scope
    if role == Role.HR:
        filters = []

        if user.region and table_name in {"employees", "employee_territories"}:
            if table_name == "employees":
                filters.append({"column": "region", "operator": "=", "value": user.region})

        if user.country and table_name == "employees":
            filters.append({"column": "country", "operator": "=", "value": user.country})

        return {
            "table": table_name,
            "filters": filters,
            "restricted": len(filters) > 0,
        }

    # Guest: public veri
    if role == Role.GUEST:
        return {
            "table": table_name,
            "filters": [],
            "restricted": False,
        }

    return {
        "table": table_name,
        "filters": [],
        "restricted": False,
    }


def apply_rls_to_rows(user: UserContext, table_name: str, rows: list[dict]) -> list[dict]:
    """
    Elimizdeki row verisini policy'ye göre filtreler.
    Şimdilik demo/test amaçlı Python seviyesinde filtre uyguluyoruz.
    """

    policy = get_rls_filters(user, table_name)
    filters = policy["filters"]

    if not filters:
        return rows

    filtered_rows = []

    for row in rows:
        matched = True

        for rule in filters:
            column = rule["column"]
            operator = rule["operator"]
            value = rule["value"]

            row_value = row.get(column)

            if operator == "=":
                if row_value != value:
                    matched = False
                    break

            elif operator == "contains":
                if row_value is None or value not in str(row_value):
                    matched = False
                    break

        if matched:
            filtered_rows.append(row)

    return filtered_rows