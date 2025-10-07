import json
import boto3
from datetime import datetime, timezone

lex_bot = boto3.client('lexv2-runtime')

BOT_ID = '48LGVHQW9V'
BOT_ALIAS_ID = 'TSTALIASID'
LOCALE_ID = 'en_US'
# there is a bug, that if I do not use fixed session_id, it will keep jump back to ask for city name.
SESSION_ID = "global-session-1"
def lambda_handler(event, context):
    print(event)
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        body = {}
    """
        the type is annoying
        set to "string" first, then can work in test, API gate way

        curl -X POST \
        -H "Content-Type: application/json" \
        -d '{"messages":[{"type":"string","unstructured":{"id":"123","text":"hi","timestamp":"2025-10-06T00:00:00Z"}}]}' \
        https://0fo5wctlub.execute-api.us-east-1.amazonaws.com/dev/chatbot
            {"messages": [{"type": "string", "unstructured": {"id": "e22445f3-bf9a-4995-bfad-76a12558e96d", "text": "I am still under development. Please come back later.", "timestamp": "2025-10-06T20:29:02.268273+00:00"}}]}%
        
        but not in frontend, the frontend can get message, and return 200 status, but no message.
        need to use unstructured
    """

    user_message = None
    if "messages" in body and len(body["messages"]) > 0:
        msg = body["messages"][0]
        if msg.get("type") == "unstructured":
            user_message = msg["unstructured"].get("text")
        elif msg.get("type") == "string":  # fallback for test
            user_message = msg["unstructured"].get("text")

    if not user_message:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "No user input provided"})
        }

    # Call Lex with a **consistent sessionId**
    lex_response = lex_bot.recognize_text(
        botId=BOT_ID,
        botAliasId=BOT_ALIAS_ID,
        localeId=LOCALE_ID,
        sessionId=SESSION_ID,
        text=user_message
    )
    print("Lex response:", lex_response)

    # Extract Lex reply
    reply_text = "Sorry, I didn’t get that."
    if "messages" in lex_response and len(lex_response["messages"]) > 0:
        reply_text = lex_response["messages"][0].get("content", reply_text)

    # Build frontend response in "unstructured" format
    response_message = {
        "messages": [
            {
                "type": "unstructured",
                "unstructured": {
                    "id": SESSION_ID,
                    "text": reply_text,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        ]
    }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        "body": json.dumps(response_message)
    }