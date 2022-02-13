from lib2to3.pytree import Base
from rest_framework.permissions import BasePermission


class CustomerPermissions(BasePermission):
    def has_permission(self, request, view):
        connected_user = request.user
        if request.method == 'GET':
            return True
        if connected_user.role == 'MANAGER':
            return True
        if connected_user.role == 'SELLER':
            if view.action == 'create' or view.action == 'update' or view.action == 'partial_update':
                return True
        return False

class ContractPermissions(BasePermission):
    def has_permission(self, request, view):
        connected_user = request.user
        if request.method == 'GET':
            return True
        if connected_user.role == 'MANAGER':
            return True
        if connected_user.role == 'SELLER':
            if view.action == 'create' or view.action == 'update' or view.action == 'partial_update':
                return True
        return False


class EventPermission(BasePermission):
    def has_permission(self, request, view):
        connected_user = request.user
        if request.method == 'GET':
            return True
        if connected_user.role == 'MANAGER':
            return True
        if connected_user.role == 'SELLER':
            if view.action == 'create':
                return True
        if connected_user.role == 'SUPPORT':
            if view.action == 'update' or view.action == 'pertial_update':
                return True
        return False