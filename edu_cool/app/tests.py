from django.test import TestCase

from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from rest_framework import status

from app.models import Course, Enrollment, Announcement, Comment

from unittest import skip

from app.cookies import have_cookies, scan_refresh_cookie

# Create your tests here.

# 1) start with the main scenario
# 2) invert and check other cases
# test cases naming: test_actor[tutor, student, non_member, anonymous]_operation[create, retrieve, update, list]_resource[course, comment, announcement,],
# if the actor is tutor ommit it so it'd be just: test_operation_resource


## use reverse to get the url using the name, to decouple it from urls changes
# https://www.django-rest-framework.org/api-guide/testing/#example


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

		self.inactive_user = User.objects.create(username='inactive_user', password='$$ATYQW#9ER&TY123456', email='user1@educool.com')

		self.inactive_user.set_password('$$ATYQW#9ER&TY123456')

		self.inactive_user.is_active = False
		
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


	@skip('no longer supported, after storing the token in httponly cookie')
	def test_jwt_token(self):

		url = '/auth/jwt/create'

		data = {'username': 'user1', 'password': '$$ATYQW#9ER&TY123456'}

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_login(self):
		
		url = '/login/'

		data = {'username': 'user1', 'password': '$$ATYQW#9ER&TY123456'}

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_invalid_username(self):
		
		url = '/login/'

		data = {'username': 'user2', 'password': '$$ATYQW#9ER&TY123456'}

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
		# auth failed err


	def test_login_invalid_password(self):
		
		url = '/login/'	

		data = {'username': 'user1', 'password': '$$ATYQW#9ER&TY654321'}

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

		# auth failed err

	# def test_login_  inactive user

	def test_inactive_user(self):

		url = '/login/'

		data = {'username': 'inactive_user', 'password': '$$ATYQW#9ER&TY123456'}

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


	def test_logout(self):

		url = '/login/'

		data = {'username': 'user1', 'password': '$$ATYQW#9ER&TY123456'}

		response = self.client.post(url, data)
		
		url = '/logout/'

		# self.client.force_authenticate(user = self.user)

		# self.client.login(username = "user1", password = "$$ATYQW#9ER&TY123456")

		response = self.client.post(url)

		print(response.content)
		
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		self.assertEqual(have_cookies(response), False)

		self.assertFalse(have_cookies(response))

		print("**********************************")

	
	def test_logout_anonymous(self):
	
		url = '/logout/'

		self.client.force_authenticate(user = None)

		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

		self.assertEqual(have_cookies(response), False)

	@skip('need to create a new function to read token from response obj first')
	# tech_debt += 1
	def test_refresh_token(self):

		url = '/login/'

		data = {'username': 'user1', 'password': '$$ATYQW#9ER&TY123456'}

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

		old_token = scan_refresh_cookie(response)

		url = '/jwt/refresh/'

		# self.client.force_authenticate(user = self.user)

		# old_refresh_token = read_token_from_cookie()

		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

		new_token = scan_refresh_cookie(response)

		self.assertNotEqual(new_token, old_token)


	@skip(' a lion doesnt concern himself with csrf checks' )
	#tech_debt += 1
	def test_csrf(self):
		# jk, i still need to search a lil bit on how to do it correctly and don't waste more time on it now
		pass
		# but basically, we make a valid req, extract the csrf and add it to the header, make another req, then assert the status


	def test_jwt_expirey(self):
		# keep itlater after installing time freezing package
		pass


class TestCourseViews(APITestCase):

	def setUp(self):

		self.tutor = User.objects.create(username='tutor', password='$$ATYQW#9ER&TY123456', email='user1@educool.com')
		
		self.course = Course.objects.create(tutor = self.tutor, title = 'course101')

		self.student = User.objects.create(username='student', password='$$ATYQW#9ER&TY123456', email='user1@educool.com')

		self.enrollment = Enrollment.objects.create(course = self.course, student = self.student)

		self.non_member = User.objects.create(username='randomuser', password='$$ATYQW#9ER&TY123456', email='user1@educool.com')
	

	def test_create_course(self):

		url = '/courses/'

		""" got a bug here because when you hit 'www.123.com/courses'
		for example you get redirected to the 'www.123.com/courses/' 
		without noticing it in the browser, 
		some how I've fallen for that before but forgot it"""

		data = {'title': 'robbing banks 101'}

		self.client.force_authenticate(user = self.tutor)

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)


	def test_anonymous_create_course(self):
		
		url = '/courses/'

		data = {'title': 'robbing banks 101'}

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


	def test_update_course(self):
		
		id = self.course.id

		url = f'/courses/{id}/'

		data = {'title': 'course102'}

		self.client.force_authenticate(user = self.tutor)

		response = self.client.put(url, data)
		
		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_student_update_course(self):
		
		id = self.course.id

		url = f'/courses/{id}/'

		data = {'title': 'course102'}

		self.client.force_authenticate(user = self.student)

		response = self.client.put(url, data)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


	def test_non_member_update_course(self):
		
		id = self.course.id

		url = f'/courses/{id}/'

		data = {'title': 'course102'}

		self.client.force_authenticate(user = self.non_member)

		response = self.client.put(url, data)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


	def test_anonymous_update_course(self):
		
		id = self.course.id

		url = f'/courses/{id}/'

		data = {'title': 'course102'}

		response = self.client.put(url, data)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


	def test_retrieve_course(self):

		id = self.course.id

		url = f'/courses/{id}/'

		self.client.force_authenticate(user = self.tutor)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_student_retrieve_course(self):

		id = self.course.id

		url = f'/courses/{id}/'

		self.client.force_authenticate(user = self.student)
		
		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_non_member_retrieve_course(self):

		id = self.course.id

		url = f'/courses/{id}/'

		self.client.force_authenticate(user = self.non_member)
		
		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_anonymous_retrieve_course(self):

		id = self.course.id

		url = f'/courses/{id}/'

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


	def test_list_courses(self):
		
		url = '/courses/'

		self.client.force_authenticate(user = self.tutor)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_student_list_courses(self):
		
		url = '/courses/'

		self.client.force_authenticate(user = self.student)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_non_member_list_courses(self):
		
		url = '/courses/'

		self.client.force_authenticate(user = self.non_member)

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_anonymous_list_courses(self):

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


	def test_non_member_create_announcement(self):
		
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
	def test_non_member_update_announcement(self):
		
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

		self.tutor = User.objects.create(username = 'mark hannah', password = 'th!s!sMyP@$$Wordd#16', email = 'johndoe@educool.com')
		
		self.course = Course.objects.create(title = 'Wall street 101', tutor = self.tutor)

		self.student = User.objects.create(username = 'jordan belfort', password = 'th!s!sMyP@$$Wordd#7795', email = 'student@educool.com')

		self.enrollment = Enrollment.objects.create(course = self.course, student = self.student)
		
		self.non_member = User.objects.create(username = 'non member', password = 'th!s!sMyP@$$Wordd#777449', email = 'random@educool.com')
		
		self.announcement = Announcement.objects.create(course = self.course, title = 'How to succeed in wall street?', content = 'your only responsibility is to put meat on the table...')
		
		self.tutor_comment = Comment.objects.create(author = self.tutor, announcement = self.announcement, content = 'Nobody, idc if it\'s warren buffet or jemmy buffet, nobody knows if the stock is gonna go up, down or in flobby circles, its all a fugazi, yk what a fugazi is???' )

		self.student_comment = Comment.objects.create(author = self.student, announcement = self.announcement, content = 'fugazy its fake')


	def test_create_comment(self):

		id = self.announcement.id
		
		url = f'/announcements/{id}/comments/'

		data = {'content': 'yeah, fugazi fugazy its wazy its woozy, its fairy dust, it never existed, it never landed its not event in the elemental chart'}

		self.client.force_authenticate(user = self.tutor)

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)


	def test_student_create_comment(self):

		id = self.announcement.id
		
		url = f'/announcements/{id}/comments/'

		data = {'content': 'Its incredible ,sir, cant tell you how excited Iam'}

		self.client.force_authenticate(user = self.student)

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)


	def test_non_member_create_comment(self):

		id = self.announcement.id
		
		url = f'/announcements/{id}/comments/'

		data = {'content': 'Just smile n dial!!!'}

		self.client.force_authenticate(user = self.non_member)

		response = self.client.post(url, data)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


	@skip('api not supported yet')
	def test_update_comment(self):
		pass
	# after several meetings with the CEO and our dev team(yes, it's still just me soloing this project, at least for now)
	# we came to agreement to limit updating resources like comments and announcements to remind our users that the 'internet is written in ink'
	# so they act accordingly, as we take our community standards very seriously for the sake of safety and healthiness of the community and our end users
	# in the next versions we might allow these methods with keeping a history of the updates, might also post a poll for our users to indicate their most wanted features
	# we also considered adding a feature to report a comment to the tutors, admins if it violates our community standards,
	# if so, this would have serious consequences including but not limited to having a nice journey to azkaban
	# have a nice...wait but what's our comm standards???! TBD


	@skip('api not supported yet')
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
