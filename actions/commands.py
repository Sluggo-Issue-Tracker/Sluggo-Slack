from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from slack import WebClient
import os, requests

from .helper import ArgumentParser

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))


@csrf_exempt
def create_ticket(request):
    data = request.POST
    channel_id = data.get("channel_id")
    text = data.get("text")
    args = ArgumentParser.parse_args(text)
    print(text)

    ticket = {
        "team_id": 0,
        "tag_id_list": [0],
        "parent_id": 0,
        "assigned_user_id": 0,
        "status_id": 0,
        "title": args.get("title", ""),
        "description": args.get("desc", ""),
        "comments": [
            {
                "owner": 0,
                "content": "string",
                "activated": "2021-01-25T00:43:16.073Z",
                "deactivated": "2021-01-25T00:43:16.073Z",
            }
        ],
    }

    client.chat_postMessage(
        channel=channel_id,
        text="Creating ticket now, woooooo",
    )
    # /ticket/create_record/
    requests.post(url="http://127.0.0.1:8000/ticket/create_record/", data=ticket)
    return HttpResponse(status=200)


@csrf_exempt
def dhelp(request):
    data = request.POST
    channel_id = data.get("channel_id")
    text = data.get("text")

    client.chat_postMessage(
        channel=channel_id,
        text="Available commands:\n\t/ticket-create\n\t/help\n\t/dhelp",
    )
    return HttpResponse(status=200)
