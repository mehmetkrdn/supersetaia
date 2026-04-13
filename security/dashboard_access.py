# security/dashboard_access.py

from security.roles import Role

ROLE_DASHBOARD_ACCESS = {

    "satis_ozet": {
        Role.ADMIN,
        Role.MANAGER,
        Role.TEAM_LEAD,
        Role.EMPLOYEE,
        Role.GUEST,
    },

    "kategori_performansi": {
        Role.ADMIN,
        Role.MANAGER,
        Role.TEAM_LEAD,
        Role.EMPLOYEE,
        Role.GUEST,
    },

    "urun_performansi": {
        Role.ADMIN,
        Role.MANAGER,
        Role.TEAM_LEAD,
        Role.EMPLOYEE,
        Role.GUEST,
    },

    "musteri_analizi": {
        Role.ADMIN,
        Role.MANAGER,
        Role.TEAM_LEAD,
    },

    "siparis_ozeti": {
        Role.ADMIN,
        Role.MANAGER,
        Role.TEAM_LEAD,
        Role.EMPLOYEE,
    },

    "calisan_satislari": {
        Role.ADMIN,
        Role.MANAGER,
        Role.TEAM_LEAD,
        Role.HR,
    }
}


def can_access_dashboard(role: Role, dashboard_name: str) -> bool:
    allowed_roles = ROLE_DASHBOARD_ACCESS.get(dashboard_name, set())
    return role in allowed_roles