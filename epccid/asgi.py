"""
ASGI config for epccid project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""




"""
import os
#new line
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddleware, AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from webid.routing import websocket_urlpatterns




os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epccid.settings')
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epccid.settings')
django.setup()

application = get_asgi_application()
import core.routing


#new line
application = ProtocolTypeRouter({
    "http":get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    )
})"""
import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epccid.settings")

application = get_asgi_application()

import webid.routing

application = ProtocolTypeRouter({
    "http": application,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(webid.routing.websocket_urlpatterns))
    ),
})