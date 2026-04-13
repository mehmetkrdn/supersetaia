from app.security.user_context import UserContext
class PermissionChecker:
    def require(self, context: UserContext, permission_code: str) -> None:
        if context.is_superadmin:
            return

        if "admin" in context.role_codes:
            return

        if permission_code not in context.permission_codes:
            raise PermissionError(f"Missing permission: {permission_code}")