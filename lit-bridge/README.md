# LIT Networking Dispatch API - Table of contents
  * [LIT API](#lit-api)
    * [Description](#description)
    * [Links](#links)
  * [Authentication & token](#authorization---login-and-token-retrive)
    * [Description](#description-0)
  * [Request New Dispatch](#request-new-dispatch)
    * [Description](#description-1)
    * [Request message](#request-message)
    * [Response message](#response-message)

- [Running in docker-compose](#running-in-docker-compose)
- [Resources](#resources)

# LIT Networking Dispatch API
### Description

Lit Bridge is used to make call to the LIT Networking Dispatch API.
The common API class include:
    
* Request New Dispatch:
    * Provide a method to request a new dispatch through API. Standard request 
information need to be provided with the API call the same as the user requesting through our web portal such as Dispatch Date/Time, Job site address, requester contact information as well as scope of work and instructions. API also accept parameters that are defined for certain customer, for MetTel, will be MetTel department, MetTel Backup department, Group Email, Max Ticket ID. If all required information is provided, new dispatch request will be generated and return the dispatch number back as response. All notification and functionality is also equivalent as if request the dispatch via the Web Portal. 
* Get Dispatch: 
    * Provide a method to check dispatch status and pull dispatch information in real-time 
through API. Response will include Dispatch Date, Dispatcher, dispatcher notes, completed time and contact information etc. Any field that available through the portal can be retrieved from this API method. 
* Update Dispatch:
    * Provide a method to modify or add notes to an open dispatch. Use this method if 
MetTel needs to provide additional notes or update to LIT Networking or even update the date/time of the dispatch if the dispatcher is not confirmed yet. All other fields allowed to be updated will be provided in the request sample code in the documentation. 
* Upload file:
    * Provide a method to Attach file to an existing Dispatch record. Use this method if need to 
upload file to the dispatch request. 

### Links

LIT DEVELOPMENT:
https://test.salesforce.com/services/oauth2/token

LIT PRODUCTION:
https://na88.salesforce.com/services/apexrest

# Authorization - Login and Token retrive

### Flow to login and get the access token

This token last 2 hours.

POST request with the following body data

### Request Login

```python
import requests

url = "https://test.salesforce.com/services/oauth2/token"
grant_type = 'password'
client_id = ''
client_secret = ''
username = ''
password = ''
security_token = ''

payload = f'grant_type={grant_type}&client_id={client_id}' \
          f'&client_secret={client_secret}' \
          f'&username={username}&password={password}{security_token}'
headers = {
  'Content-Type': 'application/x-www-form-urlencoded'
}

response = requests.request("POST", url, headers=headers, data = payload)

print(response.text.encode('utf8'))
```

### Response Login

Use 'access_token' and 'instance_url' for future requests

```json
{
    "access_token": "___ACCESS_TOKEN___",
    "instance_url": "https://cs66.salesforce.com",
    "id": "https://test.salesforce.com/id/00D0v0000008rEaEAI/0050v000002UOBIAA4",
    "token_type": "Bearer",
    "issued_at": "1586166613112",
    "signature": "TVq6kPh6LFsLm2SSR5C9kt5GDjHN55af26CHSLtdhCE="
}
```

Response with invalid login data or invalid grant_type - 400

```json
{
    "error": "invalid_grant",
    "error_description": "authentication failure"
}
```

# Request New Dispatch
### Description
Not working now.

### Request message
```
{
  "request_id": "c681c72a-9c52-4c74-bd99-53c2c973b037" (per-request generated UUID),
  "body":{
          "RequestDispatch": {
            "Date_of_Dispatch": "2016-11-16",
            "Site_Survey_Quote_Required": false,
            "Local_Time_of_Dispatch": "7AM-9AM",
            "Time_Zone_Local": "Pacific Time",
            "Turn_Up": "Yes",
            "Hard_Time_of_Dispatch_Local": "7AM-9AM",
            "Hard_Time_of_Dispatch_Time_Zone_Local": "Eastern Time",
            "Name_of_MetTel_Requester": "Test User1",
            "MetTel_Group_Email": "test@mettel.net",
            "MetTel_Requester_Email": "test@mettel.net",
            "MetTel_Department": "Customer Care",
            "MetTel_Department_Phone_Number": "1233211234",
            "Backup_MetTel_Department_Phone_Number": "1233211234",
            "Job_Site": "test",
            "Job_Site_Street": "test street",
            "Job_Site_City": "test city",
            "Job_Site_State": "test state2",
            "Job_Site_Zip_Code": "123321",
            "Scope_of_Work": "test",
            "MetTel_Tech_Call_In_Instructions": "test",
            "Special_Dispatch_Notes": "Test Create No Special Dispatch Notes to Pass Forward",
            "Job_Site_Contact_Name_and_Phone_Number": "test",
            "Information_for_Tech": "test",
            "Special_Materials_Needed_for_Dispatch": "test"
          }
  }
}
```

### Response message
```
{
  "request_id": "c681c72a-9c52-4c74-bd99-53c2c973b037"
  "body":{
             "Status": "Success",
              "Message": null,
              "Dispatch": {
                "turn_up": "Yes",
                "Time_Zone_Local": "Pacific Time",
                "Special_Materials_Needed_for_Dispatch": "test",
                "Special_Dispatch_Notes": "Test Create No Special Dispatch Notes to Pass Forward",
                "Scope_of_Work": "test",
                "Name_of_MetTel_Requester": "Test User2",
                "MetTel_Tech_Call_In_Instructions": "test",
                "MetTel_Requester_Email": "Test User2",
                "MetTel_Note_Updates": null,
                "MetTel_Max_ID": "test create method",
                "MetTel_Group_Email": "Test User2",
                "MetTel_Department_Phone_Number": "Test User2",
                "MetTel_Department": "Test User2",
                "Local_Time_of_Dispatch": null,
                "Job_Site_Zip_Code": "123324",
                "Job_Site_Street": "test street",
                "Job_Site_State": "test state",
                "Job_Site_Contact_Name_and_Phone_Number": "test",
                "Job_Site_City": "test city",
                "Job_Site": "test",
                "Information_for_Tech": "test",
                "Hard_Time_of_Dispatch_Time_Zone_Local": "Eastern Time",
                "Hard_Time_of_Dispatch_Local": "7AM-9AM",
                "Dispatch_Number": "DIS17922",
                "Date_of_Dispatch": "2016-10-13",
                "Backup_MetTel_Department_Phone_Number": "Test User2"
              },
              "APIRequestID": "a0p630000047qsIAAQ"
  }
  "status":200
}
```
# Get Dispatch
### Description
Get dispatch from LIT API 


### Request message
```
{
  "request_id": "c68EW1c72a-9c52-4c74-bd99-53c2c973b037" (per-request generated UUID),
  "body":{
            "dispatch_number": "DIS17922"
         }
}
```
### Response message
```
{   
    "request_id": "c68EW1c72a-9c52-4c74-bd99-53c2c973b037"
    "body":
            {
                "Status": "Success",
                "Message": null,
                "Dispatch": {
                    "turn_up": "Yes",
                    "Time_Zone_Local": "Pacific Time",
                    "Time_of_Check_Out": null,
                    "Time_of_Check_In": null,
                    "Tech_Off_Site": false,
                    "Tech_Mobile_Number": null,
                    "Tech_First_Name": null,
                    "Tech_Arrived_On_Site": false,
                    "Special_Materials_Needed_for_Dispatch": "test",
                    "Special_Dispatch_Notes": "Test Create No Special Dispatch Notes to Pass Forward",
                    "Site_Survey_Quote_Required": false,
                    "Scope_of_Work": "test",
                    "Name_of_MetTel_Requester": "Test User11111",
                    "MetTel_Tech_Call_In_Instructions": "test",
                    "MetTel_Requester_Email": "test@mettel.net",
                    "MetTel_Note_Updates": null,
                    "MetTel_Group_Email": "test@mettel.net",
                    "MetTel_Department_Phone_Number": "1233211234",
                    "MetTel_Department": "Customer Care",
                    "MetTel_Bruin_TicketID": null,
                    "Local_Time_of_Dispatch": null,
                    "Job_Site_Zip_Code": "123321",
                    "Job_Site_Street": "test street test 1111",
                    "Job_Site_State": "test state2",
                    "Job_Site_Contact_Name_and_Phone_Number": "test",
                    "Job_Site_City": "test city",
                    "Job_Site": "test",
                    "Information_for_Tech": "test",
                    "Hard_Time_of_Dispatch_Time_Zone_Local": "Eastern Time",
                    "Hard_Time_of_Dispatch_Local": "7AM-9AM",
                    "Dispatch_Status": "New Dispatch",
                    "Dispatch_Number": "DIS37290",
                    "Date_of_Dispatch": "2016-11-16",
                    "Close_Out_Notes": null,
                    "Backup_MetTel_Department_Phone_Number": "1233211234"
                },
                "APIRequestID": "a130v000001hIprAAE"
            }
    "status": 200
}
```

Response message with invalid Dispatch_ID - 200

```
{   
    "request_id": "c68EW1c72a-9c52-4c74-bd99-53c2c973b037"
    "body":
            {
                "Status": "error",
                "Message": "List has no rows for assignment to SObject",
                "Dispatch": null,
                "APIRequestID": "a130v000001hOk9AAE"
            }
    "status": 400 //TODO check if status code is accurate for this error return 
}  
```

# Update Dispatch
### Description

Update fields from dispatch 

### Request message

**"Dispatch_Number"** is a mandatory

```
{   
    "request_id": "86W1c72a-9c52-4c74-bd99-53c2c973b037" (per-request generated UUID),
    "body":{
              "RequestDispatch": {
                "Dispatch_Number": "DIS37290",
                "Date_of_Dispatch": "2016-11-16",
                "Site_Survey_Quote_Required": false,
                "Local_Time_of_Dispatch": "7AM-9AM",
                "Time_Zone_Local": "Pacific Time",
                "Turn_Up": "Yes",
                "Hard_Time_of_Dispatch_Local": "7AM-9AM",
                "Hard_Time_of_Dispatch_Time_Zone_Local": "Eastern Time",
                "Name_of_MetTel_Requester": "Test User11111",
                "Job_Site_Street": "test street test 1111",
                "Special_Materials_Needed_for_Dispatch": "test"
              }
    }
}
```
### Response message
```
{
    "request_id": "86W1c72a-9c52-4c74-bd99-53c2c973b037",
    "body": {
                "Status": "Success",
                "Message": null,
                "Dispatch": {
                    "turn_up": "Yes",
                    "Time_Zone_Local": "Pacific Time",
                    "Time_of_Check_Out": null,
                    "Time_of_Check_In": null,
                    "Tech_Off_Site": false,
                    "Tech_Mobile_Number": null,
                    "Tech_First_Name": null,
                    "Tech_Arrived_On_Site": false,
                    "Special_Materials_Needed_for_Dispatch": "test",
                    "Special_Dispatch_Notes": "Test Create No Special Dispatch Notes to Pass Forward",
                    "Site_Survey_Quote_Required": false,
                    "Scope_of_Work": "test",
                    "Name_of_MetTel_Requester": "Test User11111",
                    "MetTel_Tech_Call_In_Instructions": "test",
                    "MetTel_Requester_Email": "test@mettel.net",
                    "MetTel_Note_Updates": null,
                    "MetTel_Group_Email": "test@mettel.net",
                    "MetTel_Department_Phone_Number": "1233211234",
                    "MetTel_Department": "Customer Care",
                    "MetTel_Bruin_TicketID": null,
                    "Local_Time_of_Dispatch": null,
                    "Job_Site_Zip_Code": "123321",
                    "Job_Site_Street": "test street test 1111",
                    "Job_Site_State": "test state2",
                    "Job_Site_Contact_Name_and_Phone_Number": "test",
                    "Job_Site_City": "test city",
                    "Job_Site": "test",
                    "Information_for_Tech": "test",
                    "Hard_Time_of_Dispatch_Time_Zone_Local": "Eastern Time",
                    "Hard_Time_of_Dispatch_Local": "7AM-9AM",
                    "Dispatch_Status": "New Dispatch",
                    "Dispatch_Number": "DIS37290",
                    "Date_of_Dispatch": "2016-11-16",
                    "Close_Out_Notes": null,
                    "Backup_MetTel_Department_Phone_Number": "1233211234"
                },
                "APIRequestID": "a130v000001hIoAAAU"
    }
    "status": 200
}
```
# Upload File Method: 
### Description
Use this method to upload a file to an existing Dispatch Request.
Provide the Dispatch Number in the query string with the binary data in the POST request body. 
A special header filename need to be added to the http request header with 
value set to the intended file name with extension, for example “testfile.pdf”.
This filename header is required so the file can be saved with the original name 
with the correct extension to be saved correctly. 

### Request message

Headers

```
# https://cs66.salesforce.com/services/apexrest/UploadDispatchFile/___DISPATCH_ID____ HTTP/1.1
https://cs66.salesforce.com/services/apexrest/UploadDispatchFile/DIS17918 HTTP/1.1
Content-Type: application/pdf
Authorization: Bearer <Token>
filename: testword.docx
Host: cs66.salesforce.com
Content-Length: 69077
```
request message
```
{
    "request_id": "8JV0NAc72a-9c52-4c74-bd99-53c2c973b037" (per-request generated UUID),
    "body":{
             "dispatch_number":  "DIS37290"
             "payload": binary data with file content,
             "file_name": "test_txt.txt",
             "file_content_type": "application/octet-stream"
    }
}
binary data with file content
```

### Response message
```
{
  "request_id": "8JV0NAc72a-9c52-4c74-bd99-53c2c973b037" ,
  "body":{
              "Status":"Success",
              "Message":"File ID:00P63000000pcteEAA",
              "Dispatch":null,
              "APIRequestID":null
  }
  "status": 200
}
{
  "request_id": "8JV0NAc72a-9c52-4c74-bd99-53c2c973b037" ,
  "body":{
            "Status": "Success",
            "Message": "File ID:00P0v000003K1owEAC",
            "Dispatch": null,
            "APIRequestID": null
  }
  "status": 200
}

// Content-Type: application/octet-stream

{
  "request_id": "8JV0NAc72a-9c52-4c74-bd99-53c2c973b037" ,
  "body":{
            "Status": "Success",
            "Message": "File ID:00P0v000003K1p1EAC",
            "Dispatch": null,
            "APIRequestID": null
  }
  "status": 200
}

// Content-Type: application/pdf
{
  "request_id": "8JV0NAc72a-9c52-4c74-bd99-53c2c973b037" ,
  "body":{
            "Status": "Success",
            "Message": "File ID:00P0v000003K1p6EAC",
            "Dispatch": null,
            "APIRequestID": null
  }
  "status": 200
}

// Error file size too big - 200
{
  "request_id": "8JV0NAc72a-9c52-4c74-bd99-53c2c973b037" ,
  "body":{
            "Status": "error",
            "Message": "Insert failed. First exception on row 0; first error: MAXIMUM_SIZE_OF_ATTACHMENT, attachment data exceeded maximum size: [BodyLength]",
            "Dispatch": null,
            "APIRequestID": null
        }
  }
  "status": 200
}


### Session Expired - 401

# Common Errors

### Session Expired - 401

```json
[
    {
        "message": "Session expired or invalid",
        "errorCode": "INVALID_SESSION_ID"
    }
]
```


# Running in docker-compose 
`docker-compose up --build redis nats-server lit-bridge`

# Resources
<https://medium.com/@hkaraoguz/using-swaggerui-with-quart-72a3dab19273>