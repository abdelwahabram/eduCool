from django.test import TestCase

from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from rest_framework import status

from app.models import Course, Enrollment, Announcement, Comment

# Create your tests here.

# 1) start with the main scenario
# 2) invert and check other cases

class TestUserRegistration(APITestCase):

	def setUp(self):
		pass


	def test_register_user(self):

		url = '/auth/users/'

		data = {'username': 'user1', 'password': '$$ATYQW#9ER&TY123456', 'email': 'user1@educool.com'}

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		self.assertEqual(User.objects.count(), 1)


	def test_empty_username(self):

		url = '/auth/users/'

		data = {'username': '', 'password': '$$ATYQW#9ER&TY123456', 'email': 'user1@educool.com'}

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	
	def test_week_password(self):
		
		url = '/auth/users/'

		data = {'username': 'user1', 'password': '123', 'email': 'user1@educool.com'}

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class TestUserAuthentication(APITestCase):

	def setUp(self):
		
		self.user = User.objects.create(username='user1', password='$$ATYQW#9ER&TY123456', email='user1@educool.com')

		self.user.set_password('$$ATYQW#9ER&TY123456')
		
		self.user.save()
	
	# no need for thos after separating user auth and user registeration tests
	# def test_register_user(self):

	 	# url = '/auth/users/'

		# data = {'username': 'user1', 'password': '$$ATYQW#9ER&TY123456', 'email': 'user1@educool.com'}

		# response = self.client.post(url, data)

		# self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		# self.assertEqual(User.objects.count(), 1)

		# url = '/auth/jwt/create'

		# data = {'username': 'user1', 'password': '$$ATYQW#9ER&TY123456'}

		# response = self.client.post(url, data)

		# self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_jwt_token(self):

		url = '/auth/jwt/create'

		data = {'username': 'user1', 'password': '$$ATYQW#9ER&TY123456'}

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_jwt_expirey(self):
		# keep itlater after installing time freezing package
		pass


class TestCourseViews(APITestCase):
	def setUp(self):
		# course, tutor, studemt, non  member

		self.tutor = User.objects.create(username='tutor', password='$$ATYQW#9ER&TY123456', email='user1@educool.com')
		
		self.course = Course.objects.create(tutor = self.tutor, title = 'course101')

		self.student = User.objects.create(username='student', password='$$ATYQW#9ER&TY123456', email='user1@educool.com')

		# self.student.enrolled_courses.add(self.course)

		self.enrollment = Enrollment.objects.create(course = self.course, student = self.student)

		self.non_member = User.objects.create(username='randomuser', password='$$ATYQW#9ER&TY123456', email='user1@educool.com')
	

	def test_create_course_auth(self):

		url = '/courses/'

		""" got a bug here because when you hit 'www.123.com/courses'
		for example you get redirected to the 'www.123.com/courses/' 
		without noticing it in the browser, 
		some how I've fallen for that before but forgot it"""

		data = {'title': 'robbing banks 101'}

		self.client.force_authenticate(user = self.tutor)

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)


	def test_create_course_anonymous(self):
		url = '/courses/'

		data = {'title': 'robbing banks 101'}

		# self.client.force_authenticate(user = self.tutor)

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


	def test_update_course(self):
		
		id = self.course.id

		url = f'/courses/{id}/'

		data = {'title': 'course102'}

		self.client.force_authenticate(user = self.tutor)

		response = self.client.put(url, data)

		# print(response.content)
		
		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_update_course_non_tutor(self):
		id = self.course.id

		url = f'/courses/{id}/'

		data = {'title': 'course102'}

		self.client.force_authenticate(user = self.student)

		response = self.client.put(url, data)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		

		self.client.force_authenticate(user = self.non_member)

		response = self.client.put(url, data)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


		self.client.force_authenticate(user = None)

		response = self.client.put(url, data)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


	def test_retrieve_course(self):

		id = self.course.id

		url = f'/courses/{id}/'

		self.client.force_authenticate(user = self.tutor)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


		self.client.force_authenticate(user = self.student)
		
		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


		self.client.force_authenticate(user = self.non_member)
		
		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_retrieve_course_anonymous(self):

		id = self.course.id

		url = f'/courses/{id}/'

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


	def test_list_courses(self):
		url = '/courses/'

		self.client.force_authenticate(user = self.tutor)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


		self.client.force_authenticate(user = self.student)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


		self.client.force_authenticate(user = self.non_member)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

		# they should be separated in a single tc for each one ig


	def test_list_courses_anonymous(self):

		url = '/courses/'

		response = self.client.get(url)
		
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestAnnouncementViews(APITestCase):
	
	def setUp(self):
		pass


	def test_create_announcement(self):
		pass


	def test_student_create_announcement(self):
		pass


	def test_non_members_create_announcement(self):
		pass

	def test_update_announcement(self):
		pass


	def test_student_update_announcement(self):
		pass


	def test_non_members_update_announcement(self):
		pass


	def test_retrieve_announcement(self):
		pass


	def test_non_member_retrieve_announcement(self):
		pass

	
	def test_list_announcements(self):
		pass

	
	def test_non_member_list_announcements(self):
		pass


class TestCommentViews(APITestCase):

	def setUp(self):
		pass


	def test_create_comment(self):
		pass


	def test_non_member_create_comment(self):
		pass


	def test_update_comment(self):
		pass


	def test_non_author_update_comment(self):
		pass


	def test_retrieve_comment(self):
		pass


	def test_non_member_retrieve_comment(self):
		pass


	def test_list_comments(self):
		pass


	def test_non_member_list_comments(self):
		pass


class TestEnrollmentViews(APITestCase):

	def setUp(self):
		pass


	def test_enrollment(self):
		pass


	def test_tutor_enrollment(self):
		pass


	def test_current_student_enrollment(self):
		pass


	def test_retrieve_comment(self):
		pass


	def test_non_member_retrieve_enrollment(self):
		pass


	def test_list_enrollment(self):
		pass


	def test_non_tutor_list_enrollment(self):
		pass