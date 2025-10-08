from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth, helpers
import boto3
import json

region = 'us-east-1'

host = 'search-majin-chatbot-dnojun24h7dfxxmq43gh36xxxm.aos.us-east-1.on.aws'
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, region)

client = OpenSearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
)

index_name = "restaurants"
"""
def create_index(index_name):
    index_body = {
    'settings': {
        'index': {
        'number_of_shards': 4
        }
    }
    }

    response = client.indices.create(index=index_name, body=index_body)

create_index(index_name)
print()
"""
"""
with open("restaurants.json") as f:
    data = json.load(f)

restaurants = [r for sublist in data for r in sublist]

# Bulk upload
actions = [
    {
        "_index": index_name,
        "_id": r["id"],
        "_source": {
            "RestaurantID": r["id"],
            "Cuisine": r["cuisine"]
        }
    }
    for r in restaurants
]

helpers.bulk(client, actions)
print(f"Indexed {len(restaurants)} restaurants into OpenSearch")
"""
response = client.search(
    index="restaurants",   # <-- make sure your index exists
    body={
        "query": {
            "match_all": {}
        }
    }
)

print("Found:", response["hits"]["total"]["value"], "documents")
for hit in response["hits"]["hits"]:
    print(hit["_source"])
