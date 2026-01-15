from django.conf import settings

from django.contrib.auth.models import AnonymousUser

from rest_framework_simplejwt.tokens import AccessToken

from rest_framework_simplejwt.exceptions import TokenError

from django.contrib.auth.models import User

from rest_framework.exceptions import NotAuthenticated


class ChannelsJwtAuth:

	def __init__(self, app):
		# Store the ASGI application we were passed
		self.app = app

		self.cookie_name = settings.SIMPLE_JWT["AUTH_COOKIE_ACCESS"]


	async def __call__(self, scope, receive, send):

		self.scope = dict(scope)

		token = await self.get_token()

		if not token:

			raise NotAuthenticated('user not authenticated')

		try:

			token_instance = AccessToken(token)

		except:

			TokenError()

		user_id = token_instance['user_id']

		try:

			user = await User.objects.prefetch_related('my_courses').aget(pk=user_id)
		
		except:

			raise AuthenticationFailed(' no user found')

		scope['user'] = user


		# else:
		# 	# scope['user'] = AnonymousUser()
		# 	# this is just a basic version to add the user info to the scope

		return await self.app(scope, receive, send)


	async def get_token(self):

		token = self.scope["cookies"].get(self.cookie_name)

		return token

# for a better design we could rebuild this in a 'chain of responsibility' manner like dj channels AuthMiddlewareStack
# where each class handle one job and pass to the next