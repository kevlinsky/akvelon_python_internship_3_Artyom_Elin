from rest_framework import permissions

"""
    Custom Permission class which are using to give permissions for updating user model
    by the user who owns this instance or by the admin user. Additional requirement is
    authentication
"""
class UpdatedPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        print(f'Result is {request.path.split("/")[-2] == str(request.user.id)}')
        return bool((request.path.split("/")[-2] == str(request.user.id) or request.user.is_staff) and request.user.is_authenticated)
