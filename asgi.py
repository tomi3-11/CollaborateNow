# ASGI Functionality

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

from accounts.consumers import ChatConsumer 

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "collaboration_platform.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter([
            path("ws/project/<int:project_id>/", ChatConsumer.as_asgi()),
        ]),
    }
)