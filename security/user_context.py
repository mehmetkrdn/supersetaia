# security/user_context.py

from dataclasses import dataclass, field
from typing import Optional, List

from security.roles import Role


@dataclass
class UserContext:
    user_id: int
    username: str
    role: Role

    department: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None

    allowed_tables: List[str] = field(default_factory=list)
    allowed_dashboards: List[str] = field(default_factory=list)
    notes: Optional[str] = None


def build_user_context(
    user_id: int,
    username: str,
    role: Role,
    department: Optional[str] = None,
    region: Optional[str] = None,
    country: Optional[str] = None,
    allowed_tables: Optional[List[str]] = None,
    allowed_dashboards: Optional[List[str]] = None,
    notes: Optional[str] = None,
) -> UserContext:
    return UserContext(
        user_id=user_id,
        username=username,
        role=role,
        department=department,
        region=region,
        country=country,
        allowed_tables=allowed_tables or [],
        allowed_dashboards=allowed_dashboards or [],
        notes=notes,
    )