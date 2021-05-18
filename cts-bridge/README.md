# CTS Dispatch API - Table of contents
  * [CTS API](#lit-api)
    * [Description](#description)
    * [Links](#links)
  * [Endpoints](#)

- [Running in docker-compose](#running-in-docker-compose)
- [Resources](#resources)

# CTS Dispatch API

### Description

CTS Bridge is used to make call to the CTS API.
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
* Cancel Dispatch:
    * Provide a method to Attach file to an existing Dispatch record. Use this method if need to 
upload file to the dispatch request. 

CTS only provide us production environment, all the credentials are in 1password.

Check the cts_repository fields, we had a develop environment with different fields between dev and production. Now that dev environment is not available anymore.

We use the package [simple-salesforce](https://pypi.org/project/simple-salesforce/) (Uses requests so it is syncronous)

## Queries

- Get all dispatches

After run the query, we filter all the dispatches with redis, so we are sure that they belong to us.

```sql
SELECT Id,Name,API_Resource_Name__c,Billing_Invoice_Date__c,Billing_Invoice_Number__c,Billing_Total__c,Carrier__c,Carrier_ID_Num__c,Check_In_Date__c,Check_Out_Date__c,City__c,Confirmed__c,Country__c,Description__c,Duration_Onsite__c,Early_Start__c,Ext_Ref_Num__c,Finance_Notes__c,Issue_Summary__c,Lift_Delivery_Date__c,Lift_Release_Date__c,Lift_Vendor__c,Local_Site_Time__c,Account__c,Lookup_Location_Owner__c,On_Site_Elapsed_Time__c,On_Time_Auto__c,Open_Date__c,P1__c,P10__c,P10A__c,P11__c,P11A__c,P12__c,P12A__c,P13__c,P13A__c,P14__c,P14A__c,P15__c,P15A__c,P1A__c,P2__c,P2A__c,P3__c,P3A__c,P4__c,P4A__c,P5__c,P5A__c,P6__c,P6A__c,P7__c,P7A__c,P8__c,P8A__c,P9__c,P9A__c,Resource_Assigned_Timestamp__c,Resource_Email__c,Resource_Phone_Number__c,Site_Notes__c,Site_Status__c,Special_Shipping_Instructions__c,Street__c,Status__c,Resource_Trained__c,Service_Type__c,Zip__c 
FROM Service__c 
WHERE Status__c in ('Open', 'Scheduled', 'On Site', 'Completed', 'Complete Pending Collateral', 'Canceled') 
and Open_Date__c >= LAST_MONTH
```

- Get single dispatch

```sql
SELECT Id,Name,API_Resource_Name__c,Billing_Invoice_Date__c,Billing_Invoice_Number__c,Billing_Total__c,Carrier__c,Carrier_ID_Num__c,Check_In_Date__c,Check_Out_Date__c,City__c,Confirmed__c,Country__c,Description__c,Duration_Onsite__c,Early_Start__c,Ext_Ref_Num__c,Finance_Notes__c,Issue_Summary__c,Lift_Delivery_Date__c,Lift_Release_Date__c,Lift_Vendor__c,Local_Site_Time__c,Account__c,Lookup_Location_Owner__c,On_Site_Elapsed_Time__c,On_Time_Auto__c,Open_Date__c,P1__c,P10__c,P10A__c,P11__c,P11A__c,P12__c,P12A__c,P13__c,P13A__c,P14__c,P14A__c,P15__c,P15A__c,P1A__c,P2__c,P2A__c,P3__c,P3A__c,P4__c,P4A__c,P5__c,P5A__c,P6__c,P6A__c,P7__c,P7A__c,P8__c,P8A__c,P9__c,P9A__c,Resource_Assigned_Timestamp__c,Resource_Email__c,Resource_Phone_Number__c,Site_Notes__c,Site_Status__c,Special_Shipping_Instructions__c,Street__c,Status__c,Resource_Trained__c,Service_Type__c,Zip__c 
FROM Service__c 
WHERE Name = 'CTS-DISPATCH-NUMBER'
```

# Running in docker-compose 
`docker-compose up --build redis nats-server notifier cts-bridge`

