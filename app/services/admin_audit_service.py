from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


class AdminAuditService:
    def __init__(self, db: Session):
        self.db = db

    def log_action(
        self,
        action_type: str,
        user_id: int | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        detail_json: dict | None = None,
    ):
        row = AuditLog(
            user_id=user_id,
            action_type=action_type,
            target_type=target_type,
            target_id=target_id,
            detail_json=detail_json,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def list_logs(self, limit: int = 200):
        rows = (
            self.db.query(AuditLog)
            .order_by(AuditLog.id.desc())
            .limit(limit)
            .all()
        )

        result = []
        for row in rows:
            result.append({
                "id": int(row.id),
                "user_id": int(row.user_id) if getattr(row, "user_id", None) else None,
                "action_type": row.action_type,
                "target_type": getattr(row, "target_type", None),
                "target_id": str(getattr(row, "target_id", None)) if getattr(row, "target_id", None) is not None else None,
                "detail_json": getattr(row, "detail_json", None),
                "created_at": str(getattr(row, "created_at", None)) if getattr(row, "created_at", None) else None,
            })

        return result