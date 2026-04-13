from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.admin import (
    AdminUserCreateRequest,
    AdminUserUpdateRequest,
    AdminUserStatusUpdateRequest,
    AdminUserPasswordResetRequest,
    AdminUserRoleUpdateRequest,
    AdminUserScopeUpdateRequest,
    AdminUserResponse,
    AdminRoleCreateRequest,
    AdminRoleUpdateRequest,
    AdminRolePermissionUpdateRequest,
    AdminRoleResponse,
    AdminPermissionResponse,
    AdminDatasetResponse,
    AdminColumnSecurityCreateRequest,
    AdminColumnSecurityUpdateRequest,
    AdminColumnSecurityResponse,
    AdminAuditLogResponse,
)
from app.services.admin_user_service import AdminUserService
from app.services.admin_role_service import AdminRoleService
from app.services.admin_permission_service import AdminPermissionService
from app.services.admin_dataset_service import AdminDatasetService
from app.services.admin_column_security_service import AdminColumnSecurityService
from app.services.admin_audit_service import AdminAuditService

router = APIRouter()

from app.schemas.admin import (
    AdminUserPermissionUpdateRequest,
    AdminUserPermissionResponse,
)
@router.get("/users/{user_id}/permissions", response_model=list[AdminUserPermissionResponse])
def get_user_permissions(user_id: int, db: Session = Depends(get_db)):
    try:
        return AdminUserService(db).get_user_permissions(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/users/{user_id}/permissions")
def update_user_permissions(user_id: int, payload: AdminUserPermissionUpdateRequest, db: Session = Depends(get_db)):
    try:
        return AdminUserService(db).update_user_permissions(user_id, payload.permissions)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# USERS
@router.get("/users", response_model=list[AdminUserResponse])
def list_users(db: Session = Depends(get_db)):
    return AdminUserService(db).list_users()


@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        return AdminUserService(db).get_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/users", response_model=AdminUserResponse)
def create_user(payload: AdminUserCreateRequest, db: Session = Depends(get_db)):
    try:
        return AdminUserService(db).create_user(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/users/{user_id}", response_model=AdminUserResponse)
def update_user(user_id: int, payload: AdminUserUpdateRequest, db: Session = Depends(get_db)):
    try:
        return AdminUserService(db).update_user(user_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/users/{user_id}/status")
def update_user_status(user_id: int, payload: AdminUserStatusUpdateRequest, db: Session = Depends(get_db)):
    try:
        return AdminUserService(db).update_user_status(user_id, payload.is_active)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/users/{user_id}/password")
def reset_user_password(user_id: int, payload: AdminUserPasswordResetRequest, db: Session = Depends(get_db)):
    try:
        return AdminUserService(db).reset_user_password(user_id, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/users/{user_id}/roles")
def update_user_roles(user_id: int, payload: AdminUserRoleUpdateRequest, db: Session = Depends(get_db)):
    try:
        return AdminUserService(db).update_user_roles(user_id, payload.roles)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/users/{user_id}/scopes")
def update_user_scopes(user_id: int, payload: AdminUserScopeUpdateRequest, db: Session = Depends(get_db)):
    try:
        return AdminUserService(db).update_user_scopes(user_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ROLES
@router.get("/roles", response_model=list[AdminRoleResponse])
def list_roles(db: Session = Depends(get_db)):
    return AdminRoleService(db).list_roles()


@router.post("/roles", response_model=AdminRoleResponse)
def create_role(payload: AdminRoleCreateRequest, db: Session = Depends(get_db)):
    try:
        return AdminRoleService(db).create_role(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/roles/{role_id}", response_model=AdminRoleResponse)
def update_role(role_id: int, payload: AdminRoleUpdateRequest, db: Session = Depends(get_db)):
    try:
        return AdminRoleService(db).update_role(role_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/roles/{role_id}/permissions")
def update_role_permissions(role_id: int, payload: AdminRolePermissionUpdateRequest, db: Session = Depends(get_db)):
    try:
        return AdminRoleService(db).update_role_permissions(role_id, payload.permission_codes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# PERMISSIONS
@router.get("/permissions", response_model=list[AdminPermissionResponse])
def list_permissions(db: Session = Depends(get_db)):
    return AdminPermissionService(db).list_permissions()


# DATASETS
@router.get("/datasets", response_model=list[AdminDatasetResponse])
def list_datasets(db: Session = Depends(get_db)):
    return AdminDatasetService(db).list_datasets()


# COLUMN SECURITY
@router.get("/column-security", response_model=list[AdminColumnSecurityResponse])
def list_column_security(db: Session = Depends(get_db)):
    return AdminColumnSecurityService(db).list_rules()


@router.post("/column-security", response_model=AdminColumnSecurityResponse)
def create_column_security(payload: AdminColumnSecurityCreateRequest, db: Session = Depends(get_db)):
    try:
        return AdminColumnSecurityService(db).create_rule(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/column-security/{rule_id}", response_model=AdminColumnSecurityResponse)
def update_column_security(rule_id: int, payload: AdminColumnSecurityUpdateRequest, db: Session = Depends(get_db)):
    try:
        return AdminColumnSecurityService(db).update_rule(rule_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/column-security/{rule_id}")
def delete_column_security(rule_id: int, db: Session = Depends(get_db)):
    try:
        return AdminColumnSecurityService(db).delete_rule(rule_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# AUDIT
@router.get("/audit-logs", response_model=list[AdminAuditLogResponse])
def list_audit_logs(limit: int = Query(default=200, ge=1, le=1000), db: Session = Depends(get_db)):
    return AdminAuditService(db).list_logs(limit=limit)

from app.schemas.admin import AdminDatasetAccessUpdateRequest, AdminDatasetAccessResponse
from app.services.admin_dataset_access_service import AdminDatasetAccessService

@router.get("/dataset-access", response_model=list[AdminDatasetAccessResponse])
def list_dataset_access(db: Session = Depends(get_db)):
    return AdminDatasetAccessService(db).list_all()


@router.put("/dataset-access/{dataset_id}")
def update_dataset_access(dataset_id: int, payload: AdminDatasetAccessUpdateRequest, db: Session = Depends(get_db)):
    try:
        return AdminDatasetAccessService(db).replace_access(
            dataset_id=dataset_id,
            role_codes=payload.role_codes,
            user_ids=payload.user_ids,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
