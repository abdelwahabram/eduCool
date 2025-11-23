from django.conf import settings

from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTCookieAuth(JWTAuthentication, SessionAuthentication):
	
	#NOTE: another problem to learn about hear is the diamond overlapping multible inheritance problem

		# the JWTAuthentication class doesn't ensure csrf token protection
		# drf SessionAuthentication does this job by default
		# https://github.com/encode/django-rest-framework/blob/1660c22f3ad80f08c4a6eaecf2344b22d520078e/rest_framework/authentication.py#L112

		# so we can copy the function or inherit from this class
		# these two classes share the same parent BaseAuthentication
		# and there's common methods between the two parents that this class need to decide which version to inherit

		# the algo python uses to resolve this I'd describe it comparing it to the DFS algo for simplification
		# if the class has its own implementation of the method it sticks to it
		# else: iterate the parents from left -> right and once you find it use it

		#so this class is gonna inherit all the methods in the JWTAuthentication except authenticate as we've implemented here + only the ensure_csrf() from SessionAuthentication
		# copy vs inherit?? multi inheritance might be confusing for some reading the code later, like why we're using session and jwt auth classes at the same time
		# it might also be spicific to session auth that might break with jwt auth functionality but I've read the code and checked that it doesn't
		# but i didn't want to repeat code and copy blindly also, I'd take sometime reading the CSRFCheck() class and what it does

	def authenticate(self, request):
		
		# so to tweak the authsystem we need to override the authenticate method

		#https://django-rest-framework-simplejwt.readthedocs.io/en/latest/rest_framework_simplejwt.html#rest_framework_simplejwt.authentication.JWTAuthentication it returns none if auth failed or a tuple of the user and the token in case of success

		# here's how it's implemented so we can override it
		# https://github.com/jazzband/djangorestframework-simplejwt/blob/5c067b2c7e9bdf83d958a89b2841bf382c411713/rest_framework_simplejwt/authentication.py#L27C1-L27C6

		header = self.get_header(request)

		raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE_ACCESS"])
		
		if not raw_token and header:
			
			raw_token = self.get_raw_token(header)

		if not raw_token:
			
			return

		self.enforce_csrf(request)

		validated_token = self.get_validated_token(raw_token)

		return self.get_user(validated_token), validated_token


# NOTE_1: So we need to send the jwt token in httponly cookie so the client can
	# store it securely and avoid XSS attacks
	# I learned how to implement this in dj from this tutorial:
	# https://ghoveoud.ir/posts/securing-django-rest-jwt-httponly-cookie-part-1/
	# and this answer: https://stackoverflow.com/a/66248320 
	# while looking up the docs and the gh repo of django, drf, drf simple jwt, to understand why we are doing things this way, and what happens basically

	# to summ it:
	# 1) override the authentication sys, to look for the token not just in the request header, but the COOKIES dict, 
	# alternatively, we can override the middleware to extact the token from the request token and add it to the header
	# 2) the user login view authenticate the user and get a new token and send it in httponly cookie
	# the logout -> delete the cookie

# NOTE_2:
	# I wouldn't spend this time reinventing the wheel unless I have a good reason for this
	# since this is a personal project np, I've investeed this time understanding more about dj, 
	# and how to tweak the auth sys, + it's healthy sometimes to let the nerdishness kick in, 
	# I searched for a 3rd pp that does the job (httponly cookies, with csrf checks)
	# https://pypi.org/project/dj-rest-auth/
	# I'd use that alternatively, if the goal was to deliver something and meeting a deadline was a priority


