from django.shortcuts import render

from django.contrib.auth.models import User

from app.models import Course, Announcement

from app.serializers import CourseSerializer, AnnouncementSerializer, UserSerializer

from rest_framework import viewsets

# Create your views here.

# NOTE: THESE QS MIGHT CAUSE (N+1) PROBLEM SO WE NEED TO VISIT THIS LATER

class CourseViewSet(viewsets.ModelViewSet):
	"""
	Description: post, list, retreive, or delete a course with specific pk
	"""

	queryset = Course.objects.all()

	serializer_class = CourseSerializer

	def perform_create(self, serializer):
		"""
		Description: override the original method to save the current user 
		as the tutor of the course once it's created
		"""

		return serializer.save(tutor=self.request.user)
        

class AnnouncementViewSet(viewsets.ModelViewSet):
	"""
	Description: post, list: create an announcement in a course or list all announcements in this course
	retreive, or destroy: get or delete an announcement
	"""

	queryset = Announcement.objects.all()

	serializer_class = AnnouncementSerializer

	# list: courses/course_pk/announcements
	def get_queryset(self, *args, **kwargs):
		"""
		Description: override the original method to filter the announcements
		of a specific course
		"""

		course_id = self.kwargs.get("course_pk")

		try:
			course = Course.objects.get(id=course_id)
		except Course.DoesNotExist:
			raise NotFound('404 class not found')

		return self.queryset.filter(course=course)


	def perform_create(self, serializer):
		
		"""
		Description: override the original method to 
		"""

		course_id = self.kwargs.get("course_pk")

		try:

			course = Course.objects.get(id=course_id)
		except Course.DoesNotExist:
			raise NotFound('404 class not found')

		return serializer.save(course=course)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	list users or get a user account
	"""
	queryset = User.objects.all()
	serializer_class = UserSerializer
