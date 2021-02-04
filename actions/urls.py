from django.urls import include, path

from . import commands, views

urlpatterns = [
    path("commands/dhelp", commands.dhelp),
    path("commands/ticket", commands.create_ticket),
    path("commands/auth", commands.auth),
    path("callback", views.slack_callback),
    path("commands/status-check", commands.check_status)
]
