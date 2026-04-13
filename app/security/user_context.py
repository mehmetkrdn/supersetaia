from pydantic import BaseModel, Field


class UserContext(BaseModel):
    user_id: int
    username: str
    active_company_id: int | None = None

    role_codes: list[str] = Field(default_factory=list)
    permission_codes: list[str] = Field(default_factory=list)

    company_ids: list[int] = Field(default_factory=list)
    country_ids: list[int] = Field(default_factory=list)
    region_ids: list[int] = Field(default_factory=list)
    branch_ids: list[int] = Field(default_factory=list)
    department_ids: list[int] = Field(default_factory=list)
    team_ids: list[int] = Field(default_factory=list)
    customer_ids: list[int] = Field(default_factory=list)

    is_superadmin: bool = False

    def has_role(self, role_code: str) -> bool:
        return role_code in self.role_codes

    def has_permission(self, permission_code: str) -> bool:
        return permission_code in self.permission_codes