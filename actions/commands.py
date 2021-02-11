from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from slack_sdk import WebClient
import os, requests, json

from .helper import ArgumentParser, translateError
from .request_wrappers import AuthorizedRequest
from . import config

client = WebClient(token=config.SLACK_BOT_TOKEN)


@csrf_exempt
def create_ticket(request):
    required_fields = ["title"]
    TEAM_ID = 1
    ticket_url = f"{config.API_ROOT}/api/teams/{TEAM_ID}/tickets/"
    members_url = f"{config.API_ROOT}/api/teams/{TEAM_ID}/members/"

    slack_data = request.POST
    channel_id = slack_data.get("channel_id")
    args = ArgumentParser.parse_args(slack_data.get("text"))
    user_id = slack_data.get("user_id")
    api_request = AuthorizedRequest(user_id=user_id)

    if not all(field in args for field in required_fields):
        client.chat_postEphemeral(
            channel=channel_id,
            text=f'/ticket syntax error:\n\t/ticket --title "Title" [--asgn @username --desc "Description"]',
            user=user_id,
        )
        return HttpResponse(status=200)

    ticket = {
        "team_id": TEAM_ID,
        "title": args.get("title", ""),
    }
    if "asgn" in args:
        pk = -1
        try:
            response = api_request.get(url=members_url)
            users_json = response.json().get("results")
            for i in users_json:
                if i["owner"]["username"] == args["asgn"]:
                    pk = i["owner"]["id"]
                    break
            if pk != -1:
                ticket["assigned_user"] = pk

        except Exception as e:
            message = e.__str__()

    if "desc" in args:
        ticket["description"] = args["desc"]

    try:
        response = api_request.post(url=ticket_url, data=ticket)

    except Exception as e:
        message = e.__str__()

    if response.status_code != 201:
        client.chat_postEphemeral(
            channel=channel_id,
            text=f"/ticket: Internal Error: {translateError(response.json())}",
            user=user_id,
        )
        return HttpResponse(status=200)
    ticket_res = response.json()
    message = "Ticket Created:\n"
    message += f"Ticket {ticket_res['ticket_number']}: {ticket_res['title']}\n"
    message += f"Description: {ticket_res['description']}\n"
    message += f"Owner: {ticket_res['owner']['username']}\n"
    if ("asgn" in args) and (pk != -1):
        message += f"Assigned User: {ticket_res['assigned_user']['username']}"

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
    • /my-tickets _shows current tickets_
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
    user_id = data.get("user_id")
    url = f"https://slack.com/oauth/v2/authorize?user_scope=identity.basic&client_id={config.CLIENT_ID}"

    client.chat_postEphemeral(
        channel=channel_id,
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Connect slack to sluggo"},
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
                        "url": url,
                    }
                ],
            },
        ],
        text="Connect Slack to Sluggo",
        user=user_id,
    )
    return HttpResponse(status=200)


@csrf_exempt
def my_tickets(request):
    data = request.POST
    channel_id = data.get("channel_id")
    username = data.get("user_name")
    my_tickets_data = {"owner__username": username, "team_pk": 13}

    user_id = data.get("user_id")
    api_request = AuthorizedRequest(user_id=user_id)
    message = f"{username}'s current tickets:\n"

    try:
        response = api_request.get(
            url=f"http://127.0.0.1:8000/api/teams/13/tickets/", data=my_tickets_data
        )

    except Exception as e:
        message = e.__str__()

    if response.status_code != 200:
        client.chat_postEphemeral(
            channel=channel_id, text="Error, try again", user=data.get("user_id")
        )
        return HttpResponse(status=404)

    json_response = response.json()
    results = json_response.get("results")
    ticket_num = 1

    if len(results) == 0:
        client.chat_postMessage(
            channel=channel_id,
            text=f"{username} currently has no tickets",
        )
        return HttpResponse(status=200)

    for result in results:
        title = result.get("title")
        message += f"Ticket {ticket_num}: {title}\n"
        ticket_num += 1

    client.chat_postMessage(
        channel=channel_id,
        text=message,
    )

    return HttpResponse(status=200)

@csrf_exempt
def set_description(request):
    required_fields = ["desc", "id"]
    team_id = 13
    data = request.POST
    channel_id = data.get("channel_id")
    text = data.get("text")
    args = ArgumentParser.parse_args(text)
    user_id = data.get("user_id")
    api_request = AuthorizedRequest(user_id=user_id)
    ticket_desc = args.get("desc")
    ticket_id = args.get("id")
    message = f"Description for ticket {ticket_id} updated"

    if not all(field in args for field in required_fields):
        client.chat_postEphemeral(
            channel=channel_id,
            text=f'/syntax error:\n\t/set-description --desc "Description" --id "Ticket ID',
            user=user_id,
        )
        return HttpResponse(status=200)

    try:
        response = api_request.patch(
            url=f"http://127.0.0.1:8000/api/teams/{team_id}/tickets/{ticket_id}/",
            data={"description": ticket_desc}
        )
    except Exception as e:
        message = e.__str__()

    if response.status_code != 200:
        client.chat_postEphemeral(
            channel=channel_id,
            text=f"/set-description: Internal Error: {translateError(response.json())}",
            user=user_id,
        )
        return HttpResponse(status=200)

    client.chat_postMessage(channel=channel_id, text=message)
    return HttpResponse(status=200)
