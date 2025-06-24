from app.models import Course, Enrollment, Announcement, Comment

from django.contrib.auth.models import User

from rest_framework import serializers


class CourseSerializer(serializers.HyperlinkedModelSerializer):

	tutor = serializers.HyperlinkedIdentityField(read_only=True, view_name='user-detail')

	announcements = serializers.HyperlinkedIdentityField(read_only=True, view_name='announcement-list', lookup_url_kwarg = 'course_pk')
	
	students = serializers.HyperlinkedIdentityField(read_only=True, view_name='student-list', lookup_url_kwarg='course_pk')
	
	class Meta():

		model = Course
		
		fields = ['id', 'url', 'tutor', 'title', 'announcements', 'students']


class EnrollmentSerializer(serializers.HyperlinkedModelSerializer):

	course = serializers.HyperlinkedIdentityField(read_only=True, view_name='course-detail')

	student = serializers.HyperlinkedIdentityField(read_only=True, view_name='user-detail')
	
	class Meta():

		model = Enrollment
		
		fields = ['course', 'student', 'member_since']


class AnnouncementSerializer(serializers.HyperlinkedModelSerializer):
    
	course = serializers.HyperlinkedIdentityField(read_only=True, view_name='course-detail')

	comments = serializers.HyperlinkedIdentityField(read_only=True, view_name='comment-list', lookup_url_kwarg='announcement_pk')

	class Meta():
		model = Announcement
		fields = ['id', 'url', 'course', 'title', 'content', 'time', 'attachment', 'comments']
    

class CommentSerializer(serializers.HyperlinkedModelSerializer):
	
	author = serializers.HyperlinkedIdentityField(read_only=True, view_name='user-detail')
	
	announcement = serializers.HyperlinkedIdentityField(read_only=True, view_name='announcement-detail')
	
	class Meta(object):
		
		model = Comment
		
		fields = ['id', 'url', 'author', 'announcement', 'content', 'time']


class UserSerializer(serializers.HyperlinkedModelSerializer):

	enrolled_courses = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='course-detail')
	
	class Meta():
		
		model = User
		
		fields = ['id', 'url', 'username', 'my_courses', 'enrolled_courses']
