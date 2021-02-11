from django.urls import include, path

from . import commands, views

urlpatterns = [
    path("commands/dhelp", commands.dhelp),
    path("commands/ticket", commands.create_ticket),
    path("commands/auth", commands.auth),
    path("callback", views.slack_callback),
<<<<<<< HEAD
    path("commands/status-check", commands.check_status),
    path("commands/status-change", commands.change_status),
    path("commands/print_statuses", commands.print_statuses)
=======
    path("commands/my_tickets", commands.my_tickets),
    path("commands/set-description", commands.set_description),
>>>>>>> origin/main
]
