from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse, CurrentUserResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_user_context

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        result = service.login(payload.username, payload.password)
        return TokenResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=CurrentUserResponse)
def me(current_user=Depends(get_current_user_context)):
    return CurrentUserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        active_company_id=current_user.active_company_id,
        role_codes=current_user.role_codes,
        permission_codes=current_user.permission_codes,
        company_ids=current_user.company_ids,
        country_ids=current_user.country_ids,
        region_ids=current_user.region_ids,
        branch_ids=current_user.branch_ids,
        department_ids=current_user.department_ids,
        team_ids=current_user.team_ids,
        customer_ids=current_user.customer_ids,
        is_superadmin=current_user.is_superadmin,
    )