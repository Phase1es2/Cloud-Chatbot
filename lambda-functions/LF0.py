import json
import uuid
from datetime import datetime, timezone

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

    response_message = {
        "messages": [
            {
                "type": "unstructured",
                "unstructured": {
                    "id": str(uuid.uuid4()),
                    "text": "I am still under development. Please come back later.",
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
    
