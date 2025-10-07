import json
import boto3
import logging
from decimal import Decimal #dynamodb use Decimal type instead of Float

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("yelp-restaurants")

def convert_floats(obj):
    """Recursively convert all floats in dict/list to Decimal."""
    if isinstance(obj, list):
        return [convert_floats(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_floats(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj

def load_data():
    with open("restaurants.json", "r", encoding="utf-8") as f:
        jsonObject = json.load(f)

    restaurants = [r for sublist in jsonObject for r in sublist]

    logger.info(f"Uploading {len(restaurants)} restaurants to DynamoDB")

    with table.batch_writer() as batch:
        for restaurant in restaurants:
            item = convert_floats(restaurant)
            batch.put_item(Item=item)

    print(f"Successfully uploaded {len(restaurants)} restaurants to DynamoDB")

if __name__ == "__main__":
    load_data()