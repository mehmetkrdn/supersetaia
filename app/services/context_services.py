from sqlalchemy.orm import Session

from app.repositories.context_repository import ContextRepository
from app.security.user_context import UserContext


class ContextService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ContextRepository(db)

    def build_user_context(self, user_id: int) -> UserContext:
        user = self.repo.get_user(user_id)
        if not user:
            raise ValueError("User not found")

        active_company_id = self.repo.get_default_company_id(user_id)

        role_codes = []
        permission_codes = []

        if active_company_id is not None:
            role_codes = self.repo.get_role_codes(user_id, active_company_id)
            permission_codes = self.repo.get_permission_codes(user_id, active_company_id)

        return UserContext(
            user_id=user.id,
            username=user.username,
            active_company_id=active_company_id,
            role_codes=role_codes,
            permission_codes=permission_codes,
            company_ids=self.repo.get_company_ids(user_id),
            country_ids=self.repo.get_country_ids(user_id),
            region_ids=self.repo.get_region_ids(user_id),
            branch_ids=self.repo.get_branch_ids(user_id),
            department_ids=self.repo.get_department_ids(user_id),
            team_ids=self.repo.get_team_ids(user_id),
            customer_ids=self.repo.get_customer_ids(user_id),
            is_superadmin=user.is_superadmin,
        )