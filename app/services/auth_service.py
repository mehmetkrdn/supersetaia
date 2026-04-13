from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token
from app.repositories.auth_repository import AuthRepository
from app.services.context_services import ContextService


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AuthRepository(db)
        self.context_service = ContextService(db)

    def login(self, username: str, password: str) -> dict:
        user = self.repo.get_user_by_username(username)
        if not user:
            raise ValueError("Geçersiz kullanıcı adı veya şifre.")

        if not verify_password(password, user.password_hash):
            raise ValueError("Geçersiz kullanıcı adı veya şifre.")

        access_token = create_access_token(subject=str(user.id))

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    def get_current_user_context(self, user_id: int):
        return self.context_service.build_user_context(user_id)