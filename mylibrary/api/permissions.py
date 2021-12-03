from rest_framework import permissions


class AdminWriteAccessPermission(permissions.BasePermission):
    message = 'Доступ запрещен'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff


class DataAccessPermission(permissions.BasePermission):
    message = 'Доступ запрещен'

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return request.user == obj.user

        return True
