# Dining Concierge Chatbot Setup Guide

This guide walks through deploying the Dining Concierge Chatbot using **Amazon S3, API Gateway, Lambda, Lex, and SQS**.

---

## 1. Host the Frontend on S3

1. **Prepare frontend file**  
   - In the starter repo the landing page is `chat.html`.  
   - Set the index document in S3 as `chat.html`.

2. **Create an S3 bucket**  
   - Create a new S3 bucket and give it a name.  

3. **Upload files to S3**  
   - Upload the entire frontend folder into the bucket.  

4. **Enable static website hosting**  
   - Go to the **Properties** tab.  
   - Find **Static website hosting**, enable “Host a static website”.  
   - Select `chat.html` as the index document and save.  

5. **Make the bucket public**  
   - In **Permissions**, edit **Block public access** → uncheck “Block all public access”.  
   - Enable ACLs under **Object ownership**.  

6. **Test the website**  
   - Copy the bucket website endpoint URL and open it in a browser.  

---

## 2. Create API Gateway and LF0 (Init Lambda)

1. **Import Swagger definition**  
   - Go to API Gateway → choose **REST API** → import `swagger.yaml`.  
   - Use [https://editor.swagger.io/](https://editor.swagger.io/) to inspect the API.  
   - Enable **CORS** on the endpoint so the frontend can access it.  

2. **Create the init Lambda Function (LF0)**  
   - Use AWS Console to create a Python Lambda function (`LF0.py`).  
   - Test and deploy the function.  
   - In API Gateway, configure the `/chatbot` integration to invoke this Lambda (use **AWS_PROXY** integration type).  

3. **Deploy and get SDK**  
   - Deploy the API to a stage (e.g., `dev`).  
   - In API Gateway, generate the **JavaScript SDK**, download it, and replace the original one.  
   - Upload the new `apigClient.js` to S3.  
   - Go to the endpoint and test sending a message.  

---

## 3. Create Lex Bot and LF1

1. **Create a blank Lex v2 bot**  
   - Go to **Amazon Lex**, choose **Create bot**, and select:  
     - Type: **Traditional**  
     - Bot name: `DiningConciergeBot`  
     - Role: **Create a role with basic Amazon Lex permissions**  
     - Language: **English (US)**  
     - Voice interaction: **None**  

   - **GreetingIntent**  
     - Utterances: `Hi`, `Hello`  

   - **DiningSuggestionIntent**  
     - Example utterances:  
       ```
       I want to book a table
       Can you help me find a restaurant in {Location}
       I want to eat {Cuisine} food
       Find me a {Cuisine} restaurant in {Location}
       Reserve a table for {NumOfPeople}
       We have {NumOfPeople}
       My email is {EMAIL}
       ```
     - Slots:  
       - `Location`: New York, Manhattan  
       - `Cuisine`: Thai, Chinese, French, Japanese, Korean, Indian, American, Mexican  
       - `DiningTime`: AMAZON.Time  
       - `NumOfPeople`: AMAZON.Number  
       - `Email`: AMAZON.EmailAddress  
     - Prompts:  
       - *"I can help you with that, I just need a few information from you. What city are you looking for dining in?"*  
       - *"I got you. What type of cuisine do you want?"*  
       - *"What date do you want to eat?"*  
       - *"When do you want to eat?"*  
       - *"Sweet! How many people do you have in your party?"*  
       - *"Last question! What's your email so we can confirm?"*  

   - **ThankYouIntent**  
     - Utterances: `Thank you`, `Thanks`, `Appreciate`  

2. **Create LF1 Lambda Function**  
   - Lambda extracts `bot name`, `intent`, and `slot values` from `event['sessionState']['intent']`.  
   - Routes to the appropriate handler (`Greeting`, `DiningSuggestion`, `ThankYou`).  
   - **For DiningSuggestion**:  
     - In **DialogCodeHook phase**, collects values for slots (`Location`, `Date`, `DiningTime`, `NumOfPeople`, `Cuisine`, `Email`).  
     - Extracts slots safely using `safe_get()`.  
     - Once all slots are present → calls `valid_booking()` for validation.  
     - If invalid → resets that slot (`slots[violatedSlot] = None`) and returns `elicit_slot()` to re-ask.  
     - If valid → returns `delegate()` to let Lex continue.  
   - In **FulfillmentCodeHook phase**:  
     - Builds `booking_data = {location, date, time, num_people, cuisine, email}`.  
     - Serializes into JSON and sends to **Amazon SQS**.  
     - Closes the conversation with a final confirmation message.  

3. **Connect to SQS**  
   - Create a **standard queue** (leave default settings).  
   - Copy the queue URL to use in LF1.  
   - To allow Lambda to send messages, configure **IAM policy** (see `iam.json`).  

---

## 4. Integrate Lex Chatbot into Chat API

1. **Configure Lex in LF0**  
   - Get the bot’s `BOT_ID`, `BOT_ALIAS_ID`, and `LOCALE_ID`.  
   - Use a fixed `SESSION_ID` (avoids slot reset issues in Lex).  
   - Assign IAM role permissions (from `iam.json`) so LF0 can call Lex.  

2. **Lambda flow in LF0**  
   - Receives event from API Gateway.  
   - Extracts JSON body safely.  
   - Extracts `user_message` from either `unstructured` or `string`.  
   - If no text → return HTTP 400.  
   - Sends the user’s text to Lex (`recognize_text`).  
   - If Lex responds → return Lex’s message.  
   - If not → return fallback `"Sorry, I didn't get it"`.  

3. **Frontend integration**  
   - Returns Lex’s response in `unstructured` format so the frontend chat client can display it correctly.  

## 5. Use the Yelp API to collect 1000+ random restaurants from Manhattan

1. **Get Yelp API Key**  
   - Go to [Yelp Developer Portal](https://docs.developer.yelp.com/) and create an API key.  
   - Reference: [Yelp Business Search API](https://docs.developer.yelp.com/reference/v3_business_search)  

   ```
   GET https://api.yelp.com/v3/businesses/search
   ```

2. **Setup Python Script**  
   - Store your API key and configure request headers:  
     ```python
     HEADERS = {'Authorization': 'bearer %s' % API_KEY}
     YELP_SEARCH_URL = "https://api.yelp.com/v3/businesses/search"
     ```
   - Define supported cuisines and map them to Yelp category aliases:  
     ```python
     SUPPORTED_CUISINES = ['Thai', 'Chinese', 'French', 'Japanese', 'Korean', 'Indian', 'American', 'Mexican']
     YELP_API_MAP = {
         "Thai": "thai",
         "Chinese": "chinese",
         "French": "french",
         "Japanese": "japanese",
         "Korean": "korean",
         "Indian": "indpak",
         "American": "newamerican",
         "Mexican": "mexican"
     }
     ```

3. **Collect Data with Pagination**  
   - Use parameters for paginated search (max 50 results per request):  
     ```python
     PARAMETERS = {
         "categories": alias,
         "limit": 50,
         "offset": offset,
         "location": location
     }
     ```
   - Loop with increasing `offset` to collect up to 1000 results per cuisine.  
   - Use `filter_data()` to extract only the required fields:  
     - Business ID  
     - Name  
     - Address  
     - Coordinates  
     - Number of Reviews  
     - Rating  
     - Zip Code  

4. **Save Data to JSON**  
   - Deduplicate restaurants by `id` to avoid repeats.  
   - Write results to a JSON file:  
     ```python
     with open("restaurants.json", "w", encoding="utf-8") as f:
         json.dump(cleaned_data, f, indent=4, ensure_ascii=False)
     ```
5. **Set DynamoDB**
   - create "yelp-resaurants" table in DynamoDB
   - using load_dynamodb.py to upload the json file to dynamodb
   - it does not support float type, change it to Decimal

---

## 6. Set up OpenSearch for Restaurant Data

1. **Set DynamoDB**  
- Create a DynamoDB table called **`yelp-restaurants`**.  
- Use `load_dynamodb.py` to upload the `restaurants.json` file.  
- Since DynamoDB does not support float type, convert rating and coordinates to **`Decimal`** before inserting.  

2. **Set OpenSearch**  
- Create an OpenSearch (Amazon Elasticsearch) instance.  
- Enable **fine-grained access control** and set a master user with username/password.  

3. **Create Index and Upload**  
- Create an index named **`restaurants`**.  
- Use `opensearch_client.py` to filter JSON data into `RestaurantID` and `Cuisine` fields.  
- Configure AWS CLI credentials (`aws configure`) with your IAM role’s access key/secret.  
- Use the bulk helper in `opensearch_client.py` to upload the data.  

---

## 7. Build a Suggestions Model (LF2)

1. **Create LF2 (Lambda Function 2)**  
- This function is decoupled from Lex, LF0, LF1, and SQS.  
- For testing, hard-code `{"Cuisine": "Chinese"}` and use:  
  - `elastic_query(cuisine)`: Fetch up to 100 matching restaurants from OpenSearch, randomly select 5 IDs.  
  - `dynamodb_query(raw_ids)`: Use these IDs to fetch full details from DynamoDB.  
- Filter restaurant info to only include **name, address, and rating**.  

2. **Set up SES (Email Service)**  
- Go to **SES > Configuration > Identities** and create 2 identities with your emails.  
- Verify both emails (sender + receiver).  
- In LF2, create a function that sends a test email with SES.  

3. **Integrate with LF0, LF1, S3, Lex, and SQS**  
- Ensure all services from earlier sections are running.  
- Add **SQS trigger** to LF2 and update its IAM role with SQS permissions.  
- Manually send a booking request from the frontend → message goes into SQS.  
- LF2 polls SQS, queries OpenSearch + DynamoDB, and sends results via SES.  
- Format the email as:  
  ```
  Hi, here are dining suggestions for you:
  - Cuisine: Chinese
  - Date: 2025-10-10
  - Time: 18:00
  - Party size: 2

  Restaurant recommendations:
  - Xi’an Famous Foods (4.6)
    309 Amsterdam Ave, New York, NY 10023
  ```

4. **EventBridge Scheduler**  
- Set up an **EventBridge Scheduler** to invoke LF2 every minute.  
- This ensures LF2 polls the queue automatically.  
- Verify in **CloudWatch Logs** that LF2 executes every minute.  



---

With this setup:  
- The frontend is hosted on S3.  
- API Gateway + LF0 connects the frontend to Lex.  
- Lex handles intents and slot-filling with LF1.  
- Validated bookings are sent to SQS.  
