from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    TEAM_LEAD = "team_lead"
    EMPLOYEE = "employee"
    CUSTOMER = "customer"
    HR = "hr"
    GUEST = "guest"