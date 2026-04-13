from pydantic import BaseModel, EmailStr


class AdminUserCreateRequest(BaseModel):
    username: str
    email: EmailStr | None = None
    full_name: str | None = None
    password: str
    is_active: bool = True
    is_superadmin: bool = False


class AdminUserUpdateRequest(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool = True
    is_superadmin: bool = False


class AdminUserStatusUpdateRequest(BaseModel):
    is_active: bool


class AdminUserPasswordResetRequest(BaseModel):
    password: str


class AdminUserRoleItem(BaseModel):
    role_code: str
    company_id: int


class AdminUserRoleUpdateRequest(BaseModel):
    roles: list[AdminUserRoleItem]


class AdminUserScopeUpdateRequest(BaseModel):
    company_ids: list[int] = []
    country_ids: list[int] = []
    region_ids: list[int] = []
    branch_ids: list[int] = []
    department_ids: list[int] = []
    team_ids: list[int] = []
    customer_ids: list[str] = []


class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    full_name: str | None = None
    is_active: bool
    is_superadmin: bool
    role_assignments: list[dict] = []
    company_ids: list[int] = []
    country_ids: list[int] = []
    region_ids: list[int] = []
    branch_ids: list[int] = []
    department_ids: list[int] = []
    team_ids: list[int] = []
    customer_ids: list[str] = []


class AdminRoleCreateRequest(BaseModel):
    code: str
    name: str
    description: str | None = None
    priority: int = 100
    is_system: bool = False
    is_active: bool = True


class AdminRoleUpdateRequest(BaseModel):
    name: str
    description: str | None = None
    priority: int = 100
    is_system: bool = False
    is_active: bool = True


class AdminRolePermissionUpdateRequest(BaseModel):
    permission_codes: list[str]


class AdminRoleResponse(BaseModel):
    id: int
    code: str
    name: str
    description: str | None = None
    priority: int
    is_system: bool
    is_active: bool
    permission_codes: list[str] = []


class AdminPermissionResponse(BaseModel):
    id: int
    code: str
    name: str
    description: str | None = None
    is_active: bool = True


class AdminDatasetResponse(BaseModel):
    id: int
    table_name: str
    display_name: str | None = None
    contains_company_id: bool = False
    contains_country_id: bool = False
    contains_region_id: bool = False
    contains_branch_id: bool = False
    contains_department_id: bool = False
    contains_team_id: bool = False
    contains_customer_id: bool = False


class AdminColumnSecurityCreateRequest(BaseModel):
    dataset_id: int
    column_name: str
    rule_type: str
    role_code: str | None = None
    user_id: int | None = None
    is_active: bool = True


class AdminColumnSecurityUpdateRequest(BaseModel):
    rule_type: str
    role_code: str | None = None
    user_id: int | None = None
    is_active: bool = True


class AdminColumnSecurityResponse(BaseModel):
    id: int
    dataset_id: int
    column_name: str
    rule_type: str
    role_code: str | None = None
    user_id: int | None = None
    is_active: bool


class AdminAuditLogResponse(BaseModel):
    id: int
    user_id: int | None = None
    action_type: str
    target_type: str | None = None
    target_id: str | None = None
    detail_json: dict | None = None
    created_at: str | None = None

class AdminDatasetAccessUpdateRequest(BaseModel):
    dataset_id: int
    role_codes: list[str] = []
    user_ids: list[int] = []


class AdminDatasetAccessResponse(BaseModel):
    id: int
    dataset_id: int
    table_name: str
    role_code: str | None = None
    user_id: int | None = None

class AdminUserPermissionItem(BaseModel):
    permission_code: str
    allow: bool = True


class AdminUserPermissionUpdateRequest(BaseModel):
    permissions: list[AdminUserPermissionItem]


class AdminUserPermissionResponse(BaseModel):
    permission_code: str
    allow: bool