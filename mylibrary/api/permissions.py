from rest_framework import permissions


class AdminWriteAccessPermission(permissions.BasePermission):
    message = 'Доступ запрещен'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff
