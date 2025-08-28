"""
ASGI config for collaborate_now project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""



# ASGI Functionality for collaborate_now with channels

import os
import django
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path, path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "collaborate_now.settings")

django.setup()

from accounts.consumers import ChatConsumer, WhiteboardConsumer 

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter([
            path("ws/project/<int:project_id>/chat/", ChatConsumer.as_asgi()),
            path("ws/project/<int:project_id>/whiteboard/", WhiteboardConsumer.as_asgi()), # Path for whiteboard
            # re_path(r"ws/project/<int:project_id>/whiteboard/", WhiteboardConsumer.as_asgi()),
        ]),
    ),
    }
)
