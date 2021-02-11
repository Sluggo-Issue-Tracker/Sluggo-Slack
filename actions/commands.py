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
        # response = api_req.get(url=f"http://127.0.0.1:8000/api/teams/{team_id}/tickets/{ticket_id}/")
        response = api_req.get(url=f"http://127.0.0.1:8000/api/teams/{1}/tickets/{1}/")
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

    # status = response.json().get("status").get("title")
    status = response.json().get("status").get("title")
    print(status)
    client.chat_postMessage(
        channel = channel_id,
        text = f"Ticket status: {status}",
    )

    return HttpResponse(status=200)

@csrf_exempt
def change_status(request):
    data = request.POST
    channel_id = data.get("channel_id")
    text = data.get("text")
    args = ArgumentParser.parse_args(text)
    team_id = args.get("team_id")
    ticket_id = args.get("ticket_id")
    new_status = args.get("new_status")
    print(new_status)
    # new_status = "To Do"
    new_status_id = 0

    # get auth token
    user_id = data.get("user_id")
    auth_req = AuthorizedRequest(user_id=user_id)

    # get available statuses
    try:
        statuses_response = auth_req.get(url=f"http://127.0.0.1:8000/api/teams/{team_id}/statuses/")
        statuses_message = json.dumps(statuses_response.json(), indent=4)
    except Exception as e:
        statuses_message = e.__str__()

    if statuses_response.status_code != 200:
        client.chat_postEphemeral(
            channel=channel_id,
            text="Error, try again",
            user=data.get("user_id")
        )
        return HttpResponse(status=404)

    status_results = statuses_response.json().get("results")
    statuses_list = []

    # make a list if statuses and check if new status is valid
    for status in status_results:
        title = status.get("title")
        statuses_list.append(title)

    if new_status not in statuses_list:
        client.chat_postEphemeral(
            channel=channel_id,
            text=f"Invalid status, choose from: {statuses_list}",
            user=data.get("user_id")
        )
        return HttpResponse(status=404)

    # if status valid get the id 
    for status in status_results:
        if status.get("title") == new_status:
            new_status_id = status.get("id")
            print(new_status_id)

    # update the status id
    try:
        response = auth_req.patch(
            url=f"http://127.0.0.1:8000/api/teams/{team_id}/tickets/{ticket_id}/", 
            data={"status": int(new_status_id)}
            )
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

    print(response.status_code)
    response = auth_req.get(url=f"http://127.0.0.1:8000/api/teams/{team_id}/tickets/{ticket_id}/").json().get("status")
    print(response)
    
    client.chat_postMessage(
        channel = channel_id,
        text = "Ticket status updated!"
    )
    return HttpResponse(status=200)

@csrf_exempt
def print_statuses(request):
    data = request.POST
    channel_id = data.get("channel_id")
    text = data.get("text")
    args = ArgumentParser.parse_args(text)
    team_id = args.get("team_id")

    user_id = data.get("user_id")
    auth_req = AuthorizedRequest(user_id=user_id)

    try:
        response = auth_req.get(url=f"http://127.0.0.1:8000/api/teams/{1}/statuses/")
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

    print(message)

    status_results = response.json().get("results")
    status_message = f"Team {1} statuses: "

    for status in status_results:
        title = status.get("title")
        status_message += f"{title}, "

    status_message = status_message[:-2]

    client.chat_postMessage(
        channel = channel_id,
        text = status_message
    )

    return HttpResponse(status=200)


