from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from slack_sdk import WebClient
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
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": '_# Welcome to Sluggo!_ \n\nOur commands are as follows:\n • /dhelp: _display this message_\n• /ticket-create --title "My title" --desc "My Description" --asgn @username \n',
                },
            }
        ],
        text="Welcome to Sluggo!"
    )
    return HttpResponse(status=200)

@csrf_exempt
def check_status(request):
    data = request.POST
    channel_id = data.get("channel_id")
    text = data.get("text")
    print(data)
    args = ArgumentParser.parse_args(text)

    response = requests.get(url="http://127.0.0.1:8000/ticket/{}/".format(args.get("id")))
    ticket_dict = response.json()
    # status = ticket_dict["status"]

    # need oauth to access api
    # print(response.json())
    # print(ticket_dict["status"])

    client.chat_postMessage(
        channel = channel_id,
        text = "Ticket status: {}\n".format("status")
    )
    return HttpResponse(status=200)

# @csrf_exempt
# def change_status(request):
#     data = request.POST
#     channel_id = data.get("channel_id")
#     text = data.get("text")
#     args = ArgumentParser.parse_args(text)

#     response = requests.post(
#         url="http://127.0.0.1:8000/ticket/{}/".format(args.get("id")),
#         data={"status_id": args.get("status")})
    
#     client.chat_postMessage(
#         channel = channel_id
#         text = "Ticket status updated!\n"
#     )
#     return HttpResponse(status=200)


