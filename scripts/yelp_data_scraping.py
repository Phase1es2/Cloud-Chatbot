import requests
import os
import json
from datetime import datetime, timezone
from settings import (LIMITS, LOCATIONS, 
                      SUPPORTED_CUISINES, YELP_API_KEY, 
                      MAX_RESULTS, YELP_SEARCH_URL, 
                      YELP_API_MAP)
import time

# business_id = '4AErMBEoNzbk7Q8g45kKaQ'
HEADERS = {'Authorization': 'bearer %s' % YELP_API_KEY}

def write_file(business_data):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    output_file = os.path.join(BASE_DIR, "restaurants.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(business_data, f, indent=4)

def remove_duplicate(restaurants):
    seen = set()
    res = []
    for restaurant in restaurants:
        if restaurant["id"] not in seen:
            seen.add(restaurant["id"])
            res.append(restaurant)
    return res

# we only want [Business ID, Name, Address, Coordinates, Number of Reviews, Rating, Zip Code]
def filter_data(cuisine, business_data):
    cleaned_data = []
    for business in business_data.get("businesses", []):
        data = {
            "id": business.get("id"),
            "name": business.get("name"),
            "cuisine": cuisine,
            "address": ", ".join(business.get("location", {}).get("display_address", [])),
            "coordinates": business.get("coordinates", {}),
            "review_count": business.get("review_count"),
            "rating": business.get("rating"),
            "zip_code": business.get("location", {}).get("zip_code"),
            "insertedAtTimestamp": datetime.now(timezone.utc).isoformat()
        }
        cleaned_data.append(data)
    return cleaned_data

def get_restaurants(cuisine, location = LOCATIONS, max_result=MAX_RESULTS):
    alias = YELP_API_MAP.get(cuisine, cuisine.lower())
    data = []
    for offset in range(0, MAX_RESULTS, LIMITS):
        PARAMETERS = {
            'categories': alias,
            "limit": LIMITS,
            'offset': offset,
            'location': location
        }
        #make a request to the YELP API
        resp = requests.get(url = YELP_SEARCH_URL,
                            params=PARAMETERS,
                            headers=HEADERS)
        
        # Convert the JSON string'
        business_data = resp.json()
        cleaned_data = filter_data(cuisine, business_data)
        cleaned_data = remove_duplicate(cleaned_data)
        data.extend(cleaned_data)

        if len(business_data.get("businesses", [])) < LIMITS:
            break
        time.sleep(2)
    return data

if __name__ == "__main__":
    # Example usage
    cuisine_type_res = []
    for cuisine in SUPPORTED_CUISINES:
        data = get_restaurants(cuisine, "Manhattan")
        cuisine_type_res.append(data)
        print(f"{cuisine} : {len(data)} entries")
        
    write_file(cuisine_type_res)
    print("Done saving restaurants.json with data for ", len(cuisine_type_res), "cuisines")