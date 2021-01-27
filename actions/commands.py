from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from slack_sdk import WebClient
import os, requests

from .helper import ArgumentParser, OAuthAuthenticator, translateError

from .errors import error_messages

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
auth = OAuthAuthenticator(token=os.getenv("SLACK_OAUTH_ACCESS_TOKEN"))


@csrf_exempt
def create_ticket(request):
    required_fields = ["title"]

    data = request.POST
    channel_id = data.get("channel_id")
    text = data.get("text")
    args = ArgumentParser.parse_args(text)

    if not all(field in args for field in required_fields):
        client.chat_postEphemeral(
            channel=channel_id,
            text=error_messages["required_field"].format("/ticket", "--title"),
            user=data.get("user_id"),
        )
        return HttpResponse(status=200)

    ticket = {
        "team_id": 1,
        "assigned_user_id": 1,
        "title": args.get("title", ""),
        "description": args.get("desc", ""),
    }

    headers = auth.authenticate(data.get("user_id"))
    if headers is None:
        client.chat_postEphemeral(
            channel=channel_id,
            text=error_messages["auth_error"].format("/ticket"),
            user=data.get("user_id"),
        )
        return HttpResponse(status=200)

    status = requests.post(
        url="http://127.0.0.1:8000/ticket/create_record/", data=ticket, headers=headers
    )

    if status.status_code != 200:
        client.chat_postEphemeral(
            channel=channel_id,
            text=error_messages["ticket_create"].format(
                "/ticket", translateError(status.json())
            ),
            user=data.get("user_id"),
        )
        return HttpResponse(status=200)

    client.chat_postMessage(
        channel=channel_id,
        text="Ticket properly created",
    )

    return HttpResponse(status=200)


@csrf_exempt
def dhelp(request):
    data = request.POST
    channel_id = data.get("channel_id")
    text = data.get("text")
    multi_help = """
_*# Welcome to Sluggo!*_

Our commands are as follows:
    • /dhelp: _display this message_
    • /ticket-create --title "My title" --desc "My Description" --asgn @username
"""

    client.chat_postMessage(
        channel=channel_id,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": multi_help,
                },
            }
        ],
        text="Welcome to Sluggo!",
    )
    return HttpResponse(status=200)
