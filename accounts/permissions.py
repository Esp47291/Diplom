from rest_framework import permissions

from .models import User


class IsLibrarianOrAdmin(permissions.BasePermission):
    """Создание/изменение книг, авторов и выдачи — библиотекарь или админ."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return user.role in (User.Role.LIBRARIAN, User.Role.ADMIN)


class IsOwnerOrLibrarian(permissions.BasePermission):
    """Читатель видит только свои выдачи; библиотекарь — все."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser or user.role in (
            User.Role.LIBRARIAN,
            User.Role.ADMIN,
        ):
            return True
        return getattr(obj, "user_id", None) == user.id


class CanDeleteOwnBookOrStaff(permissions.BasePermission):
    """Удаление книги: создатель книги или персонал."""

    message = "Нельзя удалить книгу, которую создал другой пользователь."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.role in (User.Role.LIBRARIAN, User.Role.ADMIN):
            return True
        return getattr(obj, "created_by_id", None) == user.id
