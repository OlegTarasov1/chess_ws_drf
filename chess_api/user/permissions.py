from rest_framework import permissions

class UserManipPermission(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.user == obj or request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        else:
            return False