from django.shortcuts import render

from django.contrib.auth.models import User

from app.models import Course, Enrollment, Announcement, Comment

from app.serializers import CourseSerializer, EnrollmentSerializer, AnnouncementSerializer, UserSerializer, CommentSerializer

from app import permissions

from rest_framework import viewsets

from rest_framework.decorators import action

from rest_framework.exceptions import NotFound, PermissionDenied

from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated


class CourseViewSet(viewsets.ModelViewSet):
	"""
	Description: post, list, retreive, or delete a course with specific pk
	"""

	# queryset = Course.objects.select_related('tutor').prefetch_related('announcements').prefetch_related('students').all()
	# no, idon't think we need to fetch all these data from the db since we're not using nested serialization

	queryset = Course.objects.select_related('tutor').all()

	serializer_class = CourseSerializer
	
	# ret auth
	# post auth
	# put tutor
	# list auth


	def get_permissions(self):

		if self.action == 'update':
			permission_classes = [permissions.IsTutor]
		
		else:
			permission_classes = [IsAuthenticated]

		return [permission() for permission in permission_classes]


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

	# ret member
	# list member
	# post, put tutor


	def get_permissions(self):
		
		if self.action == 'list' or self.action == 'retrieve':
			permission_classes = [permissions.IsTutorAnnouncement | permissions.IsStudent]
		
		elif self.action == 'update':
			permission_classes = [permissions.IsTutorAnnouncement]

		return [permission() for permission in permission_classes]


	def get_object(self, *args, **kwargs):

		pk = self.kwargs.get("pk")

		return Announcement.objects.get(pk=pk)


	def get_queryset(self, *args, **kwargs):
		"""
		Description: override the original method to filter the announcements
		of a specific course in case of list operation
		"""

		pk = self.kwargs.get("pk")

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

		if self.request.user != course.tutor:
			raise PermissionDenied('only tutor can post to the group')

		return serializer.save(course=course)


class CommentViewSet(viewsets.ModelViewSet):
	
	queryset = Comment.objects.select_related('author').select_related('announcement').all()
	
	serializer_class = CommentSerializer
	
	# post, get, list => member
	# put => author

	def get_permissions(self):

		if self.action == 'update':
			permission_classes = [permissions.IsCommentAuthor]
		
		else:
			permission_classes = [permissions.IsMember]

		return [permission() for permission in permission_classes]


	def get_object(self, *args, **kwargs):

		pk = self.kwargs.get("pk")

		return Comment.objects.get(pk=pk)


	def get_queryset(self, *args, **kwargs):
		"""
		Description: override the original method to filter the comments
		of a given announcement in case of list operation
		"""

		pk = self.kwargs.get("pk")

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

		if self.request.user != announcement.course.tutor or not announcement.course.students.objects.filter(id = self.request.user.id).exists():
			raise PermissionDenied('only course members can comment')

		return serializer.save(announcement=announcement, author = self.request.user)


class EnrollmentViewSet(viewsets.ModelViewSet):

	queryset = Enrollment.objects.select_related('course').select_related('student').all()

	serializer_class = EnrollmentSerializer

	# post => not student, not tutor=> DONE
	# list => tutor
	# get => stud, tutor

	def get_permissions(self):

		if self.action == 'retrieve':
			permission_classes = [permissions.IsEnrollmentTutor | permissions.IsEnrollmentStudent]

		if self.action == 'list':
			permission_classes = [permissions.IsEnrollmentTutor]

	def perform_create(self, serializer):

		pk = self.kwargs.get('pk')

		try:
			course = Course.objects.get(id=pk)

		except Course.DoesNotExist:
			raise NotFound('404: course not found')

		if course.tutor == self.request.user:
			raise PermissionDenied('A tutor can\'t be student')

		if course.students.objects.filter(id = self.request.user.id):
			raise PermissionDenied('already joined')
			
			# NOTE: A better way to handle this is to update the model making student and course unique together

		return serializer.save(course = course, student=self.request.user)


	def get_queryset(self, *args, **kwargs):
		"""
		Description:
		override the original method to filter the students
		of a given course id in case of list operation
		"""

		pk = self.kwargs.get("pk")

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

	permission_classes = [permissions.IsUserSession]