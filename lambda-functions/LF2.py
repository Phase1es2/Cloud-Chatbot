import json
import boto3
import random
from decimal import Decimal
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth, helpers


region = "us-east-1"
# Dynamodb
dynamodb = boto3.resource("dynamodb", region_name=region)
table = dynamodb.Table("yelp-restaurants")

#ses email
ses = boto3.client("ses", region_name=region)

# opensearch
host = 'search-majin-chatbot-dnojun24h7dfxxmq43gh36xxxm.aos.us-east-1.on.aws'
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, region)

opensearch_client = OpenSearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
)

# sqs
sqs_client = boto3.client('sqs', region_name='us-east-1')
SQS_URL = 'https://sqs.us-east-1.amazonaws.com/062825750454/majin-dining-queue'

def poll_message():
    resp = sqs_client.receive_message(
        QueueUrl=SQS_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=2
    )

    if "Messages" not in resp:
        print("No messages found")
        return []
    message = []
    for msg in resp["Messages"]:
        body = json.loads(msg["Body"])
        message.append(body)

        sqs_client.delete_message(
            QueueUrl=SQS_URL,
            ReceiptHandle=msg["ReceiptHandle"]
        )
    return message


def elastic_query(cuisine):
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"Cuisine": cuisine}}
                ]
            }
        },
        "size": 100
    }
    response = opensearch_client.search(index="restaurants", body=query)
    
    ids = [hit["_source"] for hit in response["hits"]["hits"]]
    sample_ids = random.sample(ids, min(5, len(ids)))
    # print(sample_ids)
    return sample_ids

def format_email(restaurant, cuisine, date, time, party):
    lines = [
        f"Hi, here are dining suggestions for you:",
        f"- Cuisine: {cuisine}",
        f"- Date: {date}",
        f"- Time: {time}",
        f"- Party size: {party}",
        "",
        "Restaurant recommendations:\n"
    ]
    for r in restaurant:
        line = f"- {r['name']} ({r['rating']})\n  {r['address']}"
        lines.append(line)
    return "\n".join(lines)

def send_email(restaurant, cuisine, email, party, date, time):
    body_text = format_email(restaurant, cuisine, date, time, party)
    response = ses.send_email(
        Source="hyangcaa17@gmail.com", 
        Destination={
            "ToAddresses": [email],   # send to the user’s email
        },
        Message={
            "Subject": {"Data": f"Your {cuisine} dining suggestions", "Charset": "UTF-8"},
            "Body": {
                "Text": {
                    "Data": body_text,
                    "Charset": "UTF-8"
                }
            }
        }
    )
    print("Email sent! Message ID:", response["MessageId"])
    return response


def filter_list(restaurant):
    filted = []
    for r in restaurant:
        filted.append({
            "name": r["name"],
            "address": r["address"],
            "rating": r["rating"]
        })
    return filted

def convert_decimal(obj):
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj

def dynamodb_query(raw_ids):
    recommendations_list = []
    for entry in raw_ids:
        restaurant_id = entry["RestaurantID"]
        resp = table.get_item(Key={"id": restaurant_id})
        if "Item" in resp:
            item = resp["Item"]
            item = convert_decimal(item)
            recommendations_list.append(item)

    return recommendations_list

def dispath_message(sqs_message):
    cuisine = sqs_message["cuisine"]
    email = sqs_message["email"]
    party = sqs_message["num_people"]
    date = sqs_message["date"]
    time = sqs_message["time"]
    return cuisine, email, party, date, time

def lambda_handler(event, context):
    # TODO implement
    sqs_message = poll_message()[0]
    cuisine, email, party, date, time = dispath_message(sqs_message)
    # item = test_get_item()
    # email_resp = send_email()
    recommendations_list_raw = elastic_query(cuisine)
    recommendations_list = dynamodb_query(recommendations_list_raw)
    res_list = filter_list(recommendations_list)
    print(res_list)
    email_resp = send_email(recommendations_list, cuisine, email, party, date, time)
    return {
        'statusCode': 200,
        'body': json.dumps({
            "message": "Lambda exectued",
            # "restaurant": recommendations_list,
            # "search_result": search_resp,
            # "email_message_id": email_resp["MessageId"]
            "sqs_message": sqs_message
        })
    }
