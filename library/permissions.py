from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Читать могут все, изменять – только администраторы (is_staff=True)."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """
    Для записей выдачи:
    - Читать может владелец записи или админ.
    - Создавать – любой авторизованный.
    - Изменять/удалять – только админ.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user == obj.user or request.user.is_staff
        return request.user.is_staff
