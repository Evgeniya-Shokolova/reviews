from rest_framework.permissions import BasePermission, SAFE_METHODS


class RoleBasedPermission(BasePermission):
    """
    Кастомное разрешение, позволяющее управлять объектом автору,
    администратору или модератору.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and (
                obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin
            )
        )


class IsAdmin(BasePermission):
    """
    Разрешение для проверки, является ли текущий
    пользователь администратором.
    """

    def has_permission(self, request, view):
        return request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешение, дающее доступ на чтение всем,
    а администраторам на управление контентом.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and (
                request.user.is_admin
            )
        )
