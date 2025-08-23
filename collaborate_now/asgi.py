"""
ASGI config for collaborate_now project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""



# ASGI Functionality for collaborate_now with channels

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "collaborate_now.settings")

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from accounts.consumers import ChatConsumer 


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
