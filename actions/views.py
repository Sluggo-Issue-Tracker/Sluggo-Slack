"""
Views that are not part of the slash commands. These are used in the oauth flow
"""
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import authed_user as User
from . import config
import requests as req
import json, os

@csrf_exempt
def slack_callback(request):
    if hasattr(request, "GET") and (code := request.GET["code"]):
        url = f"https://slack.com/api/oauth.v2.access"
        response = req.get(url, params={
            "client_id": config.CLIENT_ID,
            "client_secret": config.CLIENT_SECRET,
            "code": code
        })
        authed_user = response.json().get("authed_user", None)

        msg = "success!"

        if authed_user:
            print(json.dumps(authed_user, indent=4))
            instance, _ = User.objects.update_or_create(
                **authed_user
            )
            instance.save()
        else:
            msg = json.dumps(response.json(), indent=4)

        return HttpResponse(status=200, content=msg)
