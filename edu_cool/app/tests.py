from django.test import TestCase

from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from rest_framework import status

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


