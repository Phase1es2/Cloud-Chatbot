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

