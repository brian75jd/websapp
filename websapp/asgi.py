
import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from websapp import routing
from channels.routing import ProtocolTypeRouter,URLRouter
from django.core.asgi import get_asgi_application
import websapp

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'websapp.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websapp.routing.websocket_urlpatterns
        )
    ),
})
