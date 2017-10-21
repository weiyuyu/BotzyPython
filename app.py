import os
import sys
import json
from yt_search import youtube_search
from datetime import datetime

import requests
from flask import Flask, request

app = Flask(__name__)

#For Youtube
# Set DEVELOPER_KEY to the API key value 
DEVELOPER_KEY = "AIzaSyDp29Ou9donbgn_N0hnzeELpuP641qAKLc"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    json_string = requests.get("https://graph.facebook.com/%s?fields=first_name&access_token=EAAa2iYe9rN0BAHB6RcQrGikXL7QfZCAwEQv3ZBCl7BFg5yibbShQTfxhraSNaE4UqZCLcbV0uKP9ADnCHA83CtvVum2K0vZB0ShmWGvdpPX4OH7YyWNT1w9gxrNdomxiEjZClfbZBcZBZAQRjCUhwNfsOyWt2VBH18zIWDALFEOWvjZA7NSKga1yw"%(sender_id))
                    
                    sender_first_name = json.load(json_string)["first_name"]
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    if "hello" in message_text.lower() or "hi" in message_text.lower():
                        send_message(sender_id, "Hi %s, my name is Botzy!"%(sender_first_name))
                    elif "youtube" in message_text.lower():
                        search_title = message_text[8:]
                        vid_ids, vid_titles = youtube_search(search_title)

                        send_message(sender_id, "Here are some results for your search")
                        for i, vid in enumerate(vid_titles):
                            send_message(sender_id, "%s: https://www.youtube.com/watch?v=%s"%(vid,vid_ids[i]))

                    else:
                        send_message(sender_id, "Roger that!")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = unicode(msg).format(*args, **kwargs)
        print u"{}: {}".format(datetime.now(), msg)
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
