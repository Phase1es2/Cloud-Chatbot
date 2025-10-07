import json
import boto3
from decimal import Decimal

# Dynamodb
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("yelp-restaurants")

#ses email
ses = boto3.client("ses", region_name="us-east-1") 

def send_email():
    response = ses.send_email(
        Source="hyangcaa17@gmail.com", 
        Destination={
            "ToAddresses": ["hy3169@nyu.edu"],  
        },
        Message={
            "Subject": {"Data": "Test Email from SES", "Charset": "UTF-8"},
            "Body": {
                "Text": {
                    "Data": "Hello! This is a test email sent via Amazon SES.",
                    "Charset": "UTF-8"
                }
            }
        }
    )
    print("Email sent! Message ID:", response["MessageId"])
    return response

def test_get_item():
    restaurants_id = "-OixbLnFLCzQclxCSbUQ8w"
    
    resp = table.get_item(Key={"id": restaurants_id})
    if "Item" in resp:
        item = resp["Item"]
        print("Restaurant found:")
        print(item)
    else:
        print("Restaurant not found.")

def lambda_handler(event, context):
    # TODO implement
    item = test_get_item()
    email_resp = send_email()
    return {
        'statusCode': 200,
        'body': json.dumps({
            "message": "Lambda exectued",
            "restaurant": item,
            "email_message_id": email_resp["MessageId"]
        })
    }
