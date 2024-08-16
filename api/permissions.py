from rest_framework.permissions import BasePermission

class IsProjectManager(BasePermission):
	def has_permission(self, request, view):
		return request.user.groups.filter(name='project_manager').exists()


class IsProjectManagerForUnsafeMethods(BasePermission):
	def has_permission(self, request, view):
		if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
			return request.user.groups.filter(name='project_manager').exists()
		return True