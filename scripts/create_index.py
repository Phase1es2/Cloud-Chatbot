index_name = "restaurants"

if not client.indices.exists(index=index_name):
    client.indices.create(
        index=index_name,
        body={
            "mappings": {
                "properties": {
                    "RestaurantID": {"type": "keyword"},
                    "Cuisine": {"type": "keyword"}
                }
            }
        }
    )
    print("Created index:", index_name)