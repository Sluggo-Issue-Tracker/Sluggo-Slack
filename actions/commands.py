from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from slack_sdk import WebClient
import os, requests, json

from .helper import ArgumentParser
from .request_wrappers import AuthorizedRequest
from . import config

client = WebClient(token=config.SLACK_BOT_TOKEN)

@csrf_exempt
def create_ticket(request):
    data = request.POST
    channel_id = data.get("channel_id")
    text = data.get("text")
    args = ArgumentParser.parse_args(text)
    print(text)

    ticket = {
        "team_id": 1,
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

    user_id = data.get("user_id")
    request = AuthorizedRequest(user_id=user_id)
    try:
        response = request.post(url="http://127.0.0.1:8000/ticket/create_record/", data=ticket)
        message = json.dumps(response.json(), indent=4)

    except Exception as e:
        message = e.__str__()

    client.chat_postMessage(
        channel=channel_id,
        text=message,
    )

    # /ticket/create_record/
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
    • /my-tickets _shows current tickets_
    • /set-description --desc "My Description" --id "Ticket ID"
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


@csrf_exempt
def auth(request):
    data = request.POST
    channel_id = data.get("channel_id")

    url = f"https://slack.com/oauth/v2/authorize?user_scope=identity.basic&client_id={config.CLIENT_ID}"

    client.chat_postMessage(
        channel=channel_id,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Connect slack to sluggo"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Connect account",
                        },
                        "url": url
                    }
                ]
            }
        ],
        text="Welcome to Sluggo!",
    )
    return HttpResponse(status=200)

@csrf_exempt
def set_description(request):
    data = request.POST
    channel_id = data.get("channel_id")
    text = data.get("text")
    args = ArgumentParser.parse_args(text)
    user_id = data.get("user_id")
    api_request = AuthorizedRequest(user_id=user_id)
    ticket_desc = args.get("desc")
    ticket_id = args.get("id")
    message = f"Description for ticket {ticket_id} updated"

    try:
        response = api_request.patch(
            url=f"http://127.0.0.1:8000/api/teams/13/tickets/{ticket_id}/",
            data={"description": ticket_desc, "team_pk": 13}
        )
    except Exception as e:
        message = e.__str__()

    if response.status_code != 200:
        client.chat_postEphemeral(
            channel=channel_id,
            text="Error, try /dhelp to see an explanation of the commands",
            user=user_id
        )
        return HttpResponse(status=404)

    client.chat_postMessage(channel=channel_id, text=message)
