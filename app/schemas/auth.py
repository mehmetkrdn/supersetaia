from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(BaseModel):
    user_id: int
    username: str
    active_company_id: int | None
    role_codes: list[str]
    permission_codes: list[str]
    company_ids: list[int]
    country_ids: list[int]
    region_ids: list[int]
    branch_ids: list[int]
    department_ids: list[int]
    team_ids: list[int]
    customer_ids: list[int]
    is_superadmin: bool