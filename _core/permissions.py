from rest_framework import permissions
from rest_framework.views import Request, View

# from users.models import User


class IsSuperUserOrNotSafeMethod(permissions.BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        return (
            request.user.is_authenticated
            and request.user.is_superuser
            or request.method not in permissions.SAFE_METHODS
        )


class IsSuperUserOrSafeMethod(permissions.BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        return (
            request.user.is_authenticated
            and request.user.is_superuser
            or request.method in permissions.SAFE_METHODS
        )


class IsSuperUserOrOwnsAccount(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: View, obj) -> bool:
        return (
            request.user.is_authenticated
            and request.user.is_superuser
            or request.method in permissions.SAFE_METHODS
            and request.user.is_authenticated
            and request.user.id == obj.id
        )


class IsSuperUserOrOwnsComment(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: View, obj) -> bool:
        return (
            request.user.is_authenticated
            and request.user.is_superuser
            or request.user.is_authenticated
            and request.user.id == obj.user_name.id
        )
