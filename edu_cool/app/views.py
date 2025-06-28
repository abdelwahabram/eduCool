from django.shortcuts import render

from django.contrib.auth.models import User

from app.models import Course, Enrollment, Announcement, Comment

from app.serializers import CourseSerializer, EnrollmentSerializer, AnnouncementSerializer, UserSerializer, CommentSerializer

from rest_framework import viewsets

from rest_framework.decorators import action

from rest_framework.exceptions import NotFound

from rest_framework.response import Response

# Create your views here.


class CourseViewSet(viewsets.ModelViewSet):
	"""
	Description: post, list, retreive, or delete a course with specific pk
	"""

	# queryset = Course.objects.select_related('tutor').prefetch_related('announcements').prefetch_related('students').all()
	# no, idon't think we need to fetch all these data from the db since we're not using nested serialization

	queryset = Course.objects.select_related('tutor').all()

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

	queryset = Announcement.objects.select_related('course').all()

	serializer_class = AnnouncementSerializer


	def get_queryset(self, *args, **kwargs):
		"""
		Description: override the original method to filter the announcements
		of a specific course in case of list operation
		"""

		pk = self.kwargs.get("pk")

		if pk is None:
			return self.queryset

		try:
			course = Course.objects.get(id=pk)
		
		except Course.DoesNotExist:
			raise NotFound('404 class not found')

		return self.queryset.filter(course=course)


	def perform_create(self, serializer):
		"""
		Description: override the original method to save the course where the announcement was poasted
		"""

		pk = self.kwargs.get("pk")

		try:
			course = Course.objects.get(id=pk)
		
		except Course.DoesNotExist:
			raise NotFound('404 class not found')

		return serializer.save(course=course)


class CommentViewSet(viewsets.ModelViewSet):
	
	queryset = Comment.objects.select_related('author').select_related('announcement').all()
	
	serializer_class = CommentSerializer


	def get_queryset(self, *args, **kwargs):
		"""
		Description: override the original method to filter the comments
		of a given announcement in case of list operation
		"""

		pk = self.kwargs.get("pk")

		if pk is None:
			return self.queryset

		try:
			announcement = Announcement.objects.get(id=pk)
		
		except Announcement.DoesNotExist:
			raise NotFound('404 announcement not found')

		return self.queryset.filter(announcement=announcement)


	def perform_create(self, serializer):
		"""
		Description: override the original method to save the parent announcement of the comment
		"""

		pk = self.kwargs.get("pk")

		try:
			announcement = Announcement.objects.get(id=pk)
		
		except Announcement.DoesNotExist:
			raise NotFound('404 announcement not found')

		return serializer.save(announcement=announcement, author = self.request.user)


class EnrollmentViewSet(viewsets.ModelViewSet):

	queryset = Enrollment.objects.select_related('course').select_related('student').all()

	serializer_class = EnrollmentSerializer


	def perform_create(self, serializer):

		pk = self.kwargs.get('pk')

		try:
			course = Course.objects.get(id=pk)

		except Course.DoesNotExist:
			raise NotFound('404: course not found')

		return serializer.save(course = course, student=self.request.user)


	def get_queryset(self, *args, **kwargs):
		"""
		Description:
		override the original method to filter the students
		of a given course id in case of list operation
		"""

		ok = self.kwargs.get("pk")

		try:
			course = Course.objects.get(id=pk)
		
		except Course.DoesNotExist:
			raise NotFound('404 class not found')

		return self.queryset.filter(course=course)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	list users or get a user account
	"""

	queryset = User.objects.prefetch_related('my_courses').prefetch_related('enrolled_courses').all()
	
	serializer_class = UserSerializer
