# ASGI Functionality

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path

from accounts.consumers import ChatConsumer 

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "collaborate_now.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter([
            # path("ws/project/<int:project_id>/", ChatConsumer.as_asgi()),
            re_path(r"ws/project/(?P<project_id>\d+)/$", ChatConsumer.as_asgi()),
        ]),
    ),
    }
)