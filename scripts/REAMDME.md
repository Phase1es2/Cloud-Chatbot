Host the frontend on S3
1. prepare frontend fiel
    in the starter repo the landing page is chat.html; set the index document in S3 as chat.html
2. create an S3 bucket
    Create S3 bucket
    give a name
3. Upload file to S3
    upload all the frontend folder to S3.
4. Enable static website hosting
    go to Properties tab, and find static website hosting, and enbale host a static website
    select chat.html as the index doucment, and save.
5. Make the bucket public
    In Permissions, edit Block public access and uncheck Block all public assess.
    Enbale ACLS unoder Ojbect ownership
6. Test the website
    copy the bucket website endpoint URL and test it.
Create API gateway, and FL0
1. import swagger definition
    go to API Gateway, choose REST API, and import the swagger.yaml.
    go to https://editor.swagger.io/ to check how to use this API
    enable CORS on the endpoint so that frontend can access
2. Create the init Lambda Fucntion
    use AWS console to create a Python lambda (LF0.py)
    Remember to test the fucntion, and deploy the fucntion.
    in the API gateway, configue the /chatbot intergration to invoke this lambda (use aws_proxy integration type)
3. Deploy and get SDK
    deploy the API to a stage dev
    In API gateway, use Generate SDK to create JavaScript client, and download it, replace the origanl one.
    upload the new apigClient.js to S3
    go to the endpoint, and send message to test.
Create Lex Bot and LF1
1. create a blank Lex v2 bot
    Go to Amazon Lex and choose creat bot, select "traditional" "create a block bot", name it as "DiningConciergeBot" also "create a role with basic Amazon Lex permissions" "select language as English (US)", and set the Voice interaction as None. This is only a test based application.

    Create GreetingIntent by giving "Hi", "Hello" as utterance
    Create DiningSuggestionIntent: 
        utterance [
            I want to book a table
            Can you help me find a restaurant in {Location}
            I want to eat {Cusine} food
            Find me a {Cusine} Restaurant in {Location}
            Reserve a table for {NumOfPeople}
            we have {NumOfPeople}
            My email is {EMAIL}
        ]
        slots [
            Location: New York, Manhattan
            Cuisine: [
                Thai
                Chinese
                French
                Japanese
                Korean
                Indian
                American
                Mexican
            ]
            DiningTime: AMAZON.Time
            NumOfPeople: AMAZON.Number
            Email: AMAZON.EmailAddress
        ]
        prompts [
            I can help you with that, I jsut need few information from you. what city are you looking for dining in?

            I got you. what type of cusine do you want?
           What date do you want to eat?
           When do you want to eat?
            Sweet! How many people do you have in your party?
            Last question! What's your email so we can confirm?
        ]
    Create ThankYouIntent by giving "Thank you", "Thanks", "Appreciate" as utterance