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

---

With this setup:  
- The frontend is hosted on S3.  
- API Gateway + LF0 connects the frontend to Lex.  
- Lex handles intents and slot-filling with LF1.  
- Validated bookings are sent to SQS.  
