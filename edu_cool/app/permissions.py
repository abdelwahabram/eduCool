from rest_framework import permissions

class IsTutor(permissions.BasePermission):

	def has_object_permission(self, request, view, obj):

		if obj.tutor != request.user:
			return False

		return True


class IsTutorAnnouncement(permissions.BasePermission):
	
	def has_object_permission(self, request, view, obj):

		if obj.course.tutor != request.user:
			return False

		return True


class IsStudent(permissions.BasePermission):


	def has_object_permission(self, request, view, obj):

		if obj.course.students.filter(student=request.user).exists():
			
			return True

		return False


class IsMember(permissions.BasePermission):
	
	def has_object_permission(self, request, view, obj):

		if obj.announcement.course.tutor == request.user:
			return True

		if obj.announcement.course.students.filter(student=request.user).exists():
			return True

		return False

	# NOTE: we can update IsTutor + IsStudent into one class also
	# or there might be another 3rd party package that can handle nested permmissions
	# mb updating the models to store the author in the announcement obj could be a good fix

class IsCommentAuthor(permissions.BasePermission):
	
	def has_object_permission(self, request, view, obj):

		if obj.author == request.user:
			return True

		return False


class IsEnrollmentTutor(permissions.BasePermission):

	def has_object_permission(self, request, view, obj):

		if obj.course.tutor == request.user:
			return True

		return False


class IsEnrollmentStudent(permissions.BasePermission):

	def has_object_permission(self, request, view, obj):

		if obj.student == request.user:
			return True

		return False
		
	
class IsUserSession(permissions.BasePermission):

	def has_object_permission(self, request, view, obj):

		if obj == request.user:
			return True

		return False

