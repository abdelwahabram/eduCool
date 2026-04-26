"""
ASGI config for edu_cool project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.sessions import CookieMiddleware

from app.routing import websocket_urlpatterns
from app.channels_auth import ChannelsJwtAuth

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_cool.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
            CookieMiddleware(ChannelsJwtAuth(URLRouter(websocket_urlpatterns)))
        ),
})
