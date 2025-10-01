import json

def lambda_handler(event, context):
    body = event.get("body")
    if body:
        body = json.loads(body)
    else:
        body = event

    print("Messages:", body.get("messages"))

    resp = {
        "messages": [
            {
                "type": "string",
                "unstructured": {
                    "id": "string",
                    "text": "Hello from Lambda!",
                    "timestamp": "string"
                }
            }
        ]
    }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(resp)
    }