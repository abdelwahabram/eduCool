from django.conf import settings

from django.contrib.auth.models import AnonymousUser

from rest_framework_simplejwt.tokens import AccessToken

from django.contrib.auth.models import User



class ChannelsJwtAuth:

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

        self.cookie_name = settings.SIMPLE_JWT["AUTH_COOKIE_ACCESS"]


    async def __call__(self, scope, receive, send):

        self.scope = dict(scope)

        token = await self.get_token()

        # print("token: ", token)

        if token:

        	token_instance = AccessToken(token)
        	user_id = token_instance['user_id']

        	# user_name = token_instance['username']
        	# print("user:", token_instance.payload)

        	user = await User.objects.aget(pk=user_id)
        	# instead of hitting the db, consider overriding the token obtain pair serializer to add tthe user name to the token payload

        	user_name = user.username

        	# print(user_name)

        	scope['user_id'] = user_id

        	scope['user_name'] = user_name

        else:

        	scope['user'] = AnonymousUser()
        	# this is just a basic version to add the user info to the scope

        return await self.app(scope, receive, send)


    async def get_token(self):

    	print("cookies", self.scope['cookies'])

    	token = self.scope["cookies"].get(self.cookie_name)

    	return token