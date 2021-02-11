from django.urls import include, path

from . import commands, views

urlpatterns = [
    path("commands/dhelp", commands.dhelp),
    path("commands/ticket", commands.create_ticket),
    path("commands/auth", commands.auth),
    path("callback", views.slack_callback),
    path("commands/my_tickets", commands.my_tickets),
    path("commands/set-description", commands.set_description),
]
