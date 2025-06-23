from django.shortcuts import render

from django.contrib.auth.models import User

from app.models import Course, Announcement, Comment

from app.serializers import CourseSerializer, AnnouncementSerializer, UserSerializer, CommentSerializer

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound

from rest_framework.response import Response

# Create your views here.

# NOTE: THESE QS MIGHT CAUSE (N+1) PROBLEM SO WE NEED TO VISIT THIS LATER

class CourseViewSet(viewsets.ModelViewSet):
	"""
	Description: post, list, retreive, or delete a course with specific pk
	"""

	queryset = Course.objects.all()

	serializer_class = CourseSerializer
	

	# def partial_update(self, request, course_pk):

	# 	course_instance = self.get_object()

	# 	serializer = CourseSerializer(course_instance)

	# 	serializer.students.add(request.user)

	# 	if serializer.is_valid():
	# 		serializer.save()
	# 		return Response(serializer.data, status=status.HTTP_200_OK)
		

	@action(detail = True, methods=['patch'])

	def join(self, request, *args, **kwargs):
		course = self.get_object()

		# print(course.students)

		course.students.add(request.user)

		serializer = CourseSerializer(course, request.data, partial=True)

		if serializer.is_valid():
			serializer.save()

			return Response(serializer)

		# if course.is_valid():
		# course.save()
		# return Response(CourseSerializer(course, request.data).data)

		# return Response()


	# NOTE: ithink updating the relation for join is redundant and inserting in many to many relation serializer isn't handy, 
	# I guess it'd be better to create a student_to_course model explicitly and whenever a student join => post request to that model


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

	# lookup_field = course

	# lookup_url_kwarg = 'course_pk'

	# list: courses/course_pk/announcements
	def get_queryset(self, *args, **kwargs):
		"""
		Description: override the original method to filter the announcements
		of a specific course in case of list operation
		"""

		course_id = self.kwargs.get("course_pk")

		if course_id is None:
			return self.queryset

		try:
			course = Course.objects.get(id=course_id)
		except Course.DoesNotExist:
			raise NotFound('404 class not found')

		return self.queryset.filter(course=course)


	def perform_create(self, serializer):
		
		"""
		Description: override the original method to save the course where the announcement was poasted
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
