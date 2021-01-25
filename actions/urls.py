from django.urls import include, path

from . import commands

urlpatterns = [
    path("commands/dhelp", commands.dhelp),
    path("commands/ticket", commands.create_ticket),
]
