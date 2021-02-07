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
def check_status(request):
    data = request.POST
    channel_id = data.get("channel_id")
    text = data.get("text")
    args = ArgumentParser.parse_args(text)
    team_id = args.get("team_id")
    ticket_id = args.get("ticket_id")

    user_id = data.get("user_id")
    api_req = AuthorizedRequest(user_id=user_id)

    try:
        response = api_req.get(url=f"http://127.0.0.1:8000/api/teams/{team_id}/tickets/{ticket_id}/")
        message = json.dumps(response.json(), indent=4)
    except Exception as e:
        message = e.__str__()

    if response.status_code != 200:
        client.chat_postEphemeral(
            channel=channel_id,
            text="Error, try again",
            user=data.get("user_id")
        )
        return HttpResponse(status=404)

    status = response.json().get("status").get("title")
    print(status)
    client.chat_postMessage(
        channel = channel_id,
        text = f"Ticket status: {status}",
    )

    return HttpResponse(status=200)

# @csrf_exempt
# def change_status(request):
#     data = request.POST
#     channel_id = data.get("channel_id")
#     text = data.get("text")
#     args = ArgumentParser.parse_args(text)
#     team_id = args.get("team_id")
#     ticket_id = args.get("ticket_id")

#     user_id = data.get("user_id")
#     api_req = AuthorizedRequest(user_id=user_id)

#     try:
#         response = api_req.get(url=f"http://127.0.0.1:8000/api/teams/{team_id}/tickets/{ticket_id}/")
#         message = json.dumps(response.json(), indent=4)
#     except Exception as e:
#         message = e.__str__()


#     response = requests.post(
#         url="http://127.0.0.1:8000/ticket/{}/".format(args.get("id")),
#         data={"status_id": args.get("status")})
    
#     client.chat_postMessage(
#         channel = channel_id
#         text = "Ticket status updated!\n"
#     )
#     return HttpResponse(status=200)


