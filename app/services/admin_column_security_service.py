from sqlalchemy.orm import Session

from app.models.column_security import ColumnSecurity
from app.models.column_rule import RoleColumnRule, UserColumnRule
from app.models.role import Role
from app.schemas.admin import (
    AdminColumnSecurityCreateRequest,
    AdminColumnSecurityUpdateRequest,
)


class AdminColumnSecurityService:
    def __init__(self, db: Session):
        self.db = db

    def _serialize(self, row: ColumnSecurity):
        role_code = None

        if getattr(row, "role_id", None):
            role = self.db.query(Role).filter(Role.id == row.role_id).first()
            if role:
                role_code = role.code

        return {
            "id": int(row.id),
            "dataset_id": int(row.dataset_id),
            "column_name": row.column_name,
            "rule_type": row.rule_type,
            "role_code": role_code,
            "user_id": int(row.user_id) if getattr(row, "user_id", None) else None,
            "is_active": bool(row.is_active),
        }

    def _serialize_role_rule(self, row: RoleColumnRule):
        role = self.db.query(Role).filter(Role.id == row.role_id).first()

        return {
            # Negatif id veriyoruz ki mevcut column_security kayıtlarıyla çakışmasın
            "id": -int(row.id),
            "dataset_id": int(row.dataset_id),
            "column_name": row.column_name,
            "rule_type": row.rule_type,
            "role_code": role.code if role else None,
            "user_id": None,
            "is_active": True,
        }

    def _serialize_user_rule(self, row: UserColumnRule):
        return {
            # Negatif ve ayrı aralık: role rule ile de çakışmasın
            "id": -(1000000 + int(row.id)),
            "dataset_id": int(row.dataset_id),
            "column_name": row.column_name,
            "rule_type": row.rule_type,
            "role_code": None,
            "user_id": int(row.user_id),
            "is_active": True,
        }

    def list_rules(self):
        # 1) Önce mevcut sistem aynen çalışsın
        rows = self.db.query(ColumnSecurity).order_by(ColumnSecurity.id.asc()).all()
        if rows:
            return [self._serialize(row) for row in rows]

        # 2) Eğer column_security boşsa fallback olarak gerçek rule tablolarını göster
        role_rows = (
            self.db.query(RoleColumnRule)
            .order_by(RoleColumnRule.id.asc())
            .all()
        )
        user_rows = (
            self.db.query(UserColumnRule)
            .order_by(UserColumnRule.id.asc())
            .all()
        )

        result = []
        result.extend(self._serialize_role_rule(row) for row in role_rows)
        result.extend(self._serialize_user_rule(row) for row in user_rows)
        return result

    def create_rule(self, payload: AdminColumnSecurityCreateRequest):
        role_id = None
        # Eğer role_code varsa rolü bul, yoksa user_id kullanılacak demektir
        if payload.role_code:
            role = self.db.query(Role).filter(Role.code == payload.role_code).first()
            if not role:
                raise ValueError("Rol bulunamadı.")
            role_id = role.id

        # Eğer hem rol hem user yoksa hata ver (isteğe bağlı güvenlik önlemi)
        if not role_id and not payload.user_id:
            raise ValueError("Kural bir role veya kullanıcıya atanmalıdır.")

        row = ColumnSecurity(
            dataset_id=payload.dataset_id,
            column_name=payload.column_name,
            rule_type=payload.rule_type,
            role_id=role_id,
            user_id=payload.user_id,
            is_active=payload.is_active,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._serialize(row)

    def update_rule(self, rule_id: int, payload: AdminColumnSecurityUpdateRequest):
        row = self.db.query(ColumnSecurity).filter(ColumnSecurity.id == rule_id).first()
        if not row:
            raise ValueError("Kural bulunamadı.")

        role_id = None
        if payload.role_code:
            role = self.db.query(Role).filter(Role.code == payload.role_code).first()
            if not role:
                raise ValueError("Rol bulunamadı.")
            role_id = role.id

        row.rule_type = payload.rule_type
        row.role_id = role_id
        row.user_id = payload.user_id
        row.is_active = payload.is_active

        self.db.commit()
        self.db.refresh(row)
        return self._serialize(row)

    def delete_rule(self, rule_id: int):
        row = self.db.query(ColumnSecurity).filter(ColumnSecurity.id == rule_id).first()
        if not row:
            raise ValueError("Kural bulunamadı.")

        self.db.delete(row)
        self.db.commit()
        return {"status": "ok"}