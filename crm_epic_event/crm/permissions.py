from rest_framework.permissions import BasePermission


class CustomerPermissions(BasePermission):
    def has_permission(self, request, view):
        """
        Every connected user can read CustomerViewset.
        A MANAGER can do everything.
        A SELLER can create or update an instance.
        """
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
        """
        Every connected user can read ContractViewset.
        A MANAGER can do everything.
        A SELLER can create or update an instance
        """
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
        """
        Every connected user can read ContractViewset.
        A MANAGER can do everything except create an instance.
        A SUPPORT member can update an instance.
        """
        connected_user = request.user
        if request.method == 'GET':
            return True
        if connected_user.role == 'MANAGER':
            if view.action == 'create':
                return False
            return True
        if connected_user.role == 'SELLER':
            if view.action == 'create':
                return True
        if connected_user.role == 'SUPPORT':
            if view.action == 'update' or view.action == 'partial_update':
                return True
        return False