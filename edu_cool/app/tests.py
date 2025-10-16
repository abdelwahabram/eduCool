from django.test import TestCase

from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from rest_framework import status

from app.models import Course, Enrollment, Announcement, Comment

from unittest import skip

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

		self.tutor = User.objects.create(username = 'tutor', password = 'th!s!sMyP@$$Wordd#16', email = 'tutor@educool.com')
		
		self.course = Course.objects.create(title = 'course101', tutor = self.tutor)

		self.student = User.objects.create(username = 'student', password = 'th!s!sMyP@$$Wordd#7795', email = 'student@educool.com')

		self.enrollment = Enrollment.objects.create(course = self.course, student = self.student)
		
		self.non_member = User.objects.create(username = 'random', password = 'th!s!sMyP@$$Wordd#777449', email = 'random@educool.com')
		
		self.announcement = Announcement.objects.create(course = self.course, title = 'congrats', content = '50 pts 4 ev1')


	def test_create_announcement(self):

		id = self.course.id

		url = f'/courses/{id}/announcements/'

		data = {'title': 'new annoncemnt', 'content': 'welcome'}

		self.client.force_authenticate(user = self.tutor)

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)


	def test_student_create_announcement(self):
		
		id = self.course.id

		url = f'/courses/{id}/announcements/'

		data = {'title': 'new annoncemnt', 'content': 'welcome'}

		self.client.force_authenticate(user = self.student)

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


	def test_non_members_create_announcement(self):
		
		id = self.course.id

		url = f'/courses/{id}/announcements/'

		data = {'title': 'new annoncemnt', 'content': 'welcome'}

		self.client.force_authenticate(user = self.non_member)

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


	def test_anonymous_create_announcement(self):

		id = self.course.id

		url = f'/courses/{id}/announcements/'

		data = {'title': 'new annoncemnt', 'content': 'welcome'}

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


	# NOTE: i think if we aren't gonna support updating anncments,
	# we should assert that the method isn't allowed, and so with other methods like deleting other resources
	# we aren't limited to customer requirements or and i didn't document how I imagined the mvp here
	# i decided to just build something and start it
	# so it keep changing, this is some sort of hindsight bias i think, np we're learning

	
	@skip('api not built')
	def test_update_announcement(self):
		
		id = self.announcement.id

		url = f'/announcements/{id}/'

		new_title = 'new annoncemnt22222'

		new_content = 'welcome2222'

		data = {'title': new_title, 'content': new_content}

		self.client.force_authenticate(user = self.tutor)

		response = self.client.put(url, data)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

		self.assertEqual(self.announcement.title, new_title)

		self.assertEqual(self.announcement.content, new_content)


	@skip('api not built')
	def test_student_update_announcement(self):
		
		id = self.announcement.id

		url = f'/announcements/{id}/'

		old_title = self.announcement.title

		old_content = self.announcement.content

		new_title = 'new annoncemnt22222'

		new_content = 'welcome2222'

		data = {'title': new_title, 'content': new_content}

		self.client.force_authenticate(user = self.student)

		response = self.client.put(url, data)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

		self.assertEqual(self.announcement.title, old_title)

		self.assertEqual(self.announcement.content, old_content)


	@skip('api not built')
	def test_non_members_update_announcement(self):
		
		id = self.announcement.id

		url = f'/announcements/{id}/'

		old_title = self.announcement.title

		old_content = self.announcement.content

		new_title = 'new annoncemnt22222'

		new_content = 'welcome2222'

		data = {'title': new_title, 'content': new_content}

		response = self.client.put(url, data)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

		self.assertEqual(self.announcement.title, old_title)

		self.assertEqual(self.announcement.content, old_content)


		self.client.force_authenticate(user = self.non_member)

		response = self.client.put(url, data)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

		self.assertEqual(self.announcement.title, old_title)

		self.assertEqual(self.announcement.content, old_content)


	def test_retrieve_announcement(self):

		id = self.announcement.id

		url = f'/announcements/{id}/'

		self.client.force_authenticate(user = self.tutor)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_student_retrieve_announcement(self):
		
		id = self.announcement.id

		url = f'/announcements/{id}/'
		
		self.client.force_authenticate(user = self.student)
		
		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)		


	def test_non_member_retrieve_announcement(self):

		id = self.announcement.id

		url = f'/announcements/{id}/'

		self.client.force_authenticate(user = self.non_member)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


	def test_anonymous_retrieve_announcement(self):

		id = self.announcement.id

		url = f'/announcements/{id}/'

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)	

	
	def test_list_announcements(self):
		
		id = self.course.id

		url = f'/courses/{id}/announcements/'

		self.client.force_authenticate(user = self.tutor)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_student_list_announcements(self):

		id = self.course.id

		url = f'/courses/{id}/announcements/'

		self.client.force_authenticate(user = self.student)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
	

	def test_non_member_list_announcements(self):
		
		id = self.course.id

		url = f'/courses/{id}/announcements/'

		self.client.force_authenticate(user = self.non_member)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


	def test_anonymous_list_announcements(self):
		
		id = self.course.id

		url = f'/courses/{id}/announcements/'

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestCommentViews(APITestCase):

	def setUp(self):
		# tutor, std, non mem
		# class ,announcement, cmnt

		self.tutor = User.objects.create(username = 'mr john doe', password = 'th!s!sMyP@$$Wordd#16', email = 'johndoe@educool.com')
		
		self.course = Course.objects.create(title = 'loremipsum 101', tutor = self.tutor)

		self.student = User.objects.create(username = 'stdnt john doe', password = 'th!s!sMyP@$$Wordd#7795', email = 'student@educool.com')

		self.enrollment = Enrollment.objects.create(course = self.course, student = self.student)
		
		self.non_member = User.objects.create(username = 'random', password = 'th!s!sMyP@$$Wordd#777449', email = 'random@educool.com')
		
		self.announcement = Announcement.objects.create(course = self.course, title = 'loremipsum', content = 'loremipsum loremipsum loremipsum')
		
		self.tutor_comment = Comment.objects.create(author = self.tutor, announcement = self.announcement, content = 'loremipsum1 loremipsum1')

		self.student_comment = Comment.objects.create(author = self.student, announcement = self.announcement, content = 'loremipsum2 loremipsum2 loremipsum2')


	def test_create_comment(self):

		id = self.announcement.id
		
		url = f'/announcements/{id}/comments/'

		data = {'content': 'new comment'}

		self.client.force_authenticate(user = self.tutor)

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)


	def test_student_create_comment(self):

		id = self.announcement.id
		
		url = f'/announcements/{id}/comments/'

		data = {'content': 'new comment'}

		self.client.force_authenticate(user = self.student)

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)


	def test_non_member_create_comment(self):

		id = self.announcement.id
		
		url = f'/announcements/{id}/comments/'

		data = {'content': 'new comment'}

		self.client.force_authenticate(user = self.non_member)

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


	def test_update_comment(self):
		pass


	def test_non_author_update_comment(self):
		pass


	def test_retrieve_comment(self):
		
		id = self.tutor_comment.id

		url = f'/comments/{id}/'

		self.client.force_authenticate(user = self.tutor)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_student_retrieve_comment(self):
		
		id = self.tutor_comment.id

		url = f'/comments/{id}/'

		self.client.force_authenticate(user = self.student)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_non_member_retrieve_comment(self):

		id = self.tutor_comment.id

		url = f'/comments/{id}/'

		self.client.force_authenticate(user = self.non_member)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


	def test_anonymous_retrieve_comment(self):
		
		id = self.tutor_comment.id

		url = f'/comments/{id}/'

		# self.client.force_authenticate(user = )

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


	def test_list_comments(self):

		id = self.announcement.id

		url = f'/announcements/{id}/comments/'

		self.client.force_authenticate(user = self.tutor)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_student_list_comments(self):

		id = self.announcement.id

		url = f'/announcements/{id}/comments/'

		self.client.force_authenticate(user = self.student)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_non_member_list_comments(self):

		id = self.announcement.id

		url = f'/announcements/{id}/comments/'

		self.client.force_authenticate(user = self.non_member)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


	def test_anonymous_list_comments(self):

		id = self.announcement.id

		url = f'/announcements/{id}/comments/'

		# self.client.force_authenticate(user = )

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


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