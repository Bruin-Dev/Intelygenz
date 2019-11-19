# **ALGORITHM**
##### *OUTAGE_DETECTOR* (t = 40 min \[Time needed to get the list of all edges\])
- Restore all jobs from _EDGES_QUARANTINE_ (just at the beginning)
- Claim all the edges
- For each edge:
	- Claim status
	- Check status
		- If is OFFLINE, or any of its links are DISCONNECTED:
		    - Add a new QUARANTINE_JOB in APScheduler to check if the edge is still in outage situation after 10 minutes
		    - Add outage candidate to _EDGES_QUARANTINE_ with expire = quarantine_time + 5 minutes

##### *QUARANTINE_JOB* (t= 10 min from outage detection)
- Check edge status:
	- If the edge or any of the links is still in an outage condition and there is no ticket for it:
	    - Add it to _EDGES_TO_REPORT_

##### *OUTAGE_REPORT* (t = 60 min)
- Compose an email with all the edges from _EDGES_TO_REPORT_ at the moment of time defined
- Send the email
- Clear _EDGES_TO_REPORT_

#### Additional info
Stores of Redis:
- _EDGES_QUARANTINE_
- _EDGES_TO_REPORT_

# **INTERNAL WORKING**
##### *TEMPLATE RENDERER SERVICE OUTAGE REPORT* 

In the module **service_outage_report_template_renderer** the function *_compose_email* receives a list composed of the 
dicts with the info of the edges which have to be reported.
The function has optional arguments:
- **fields** is a list with the names of the fields which are in the table with the results
- **fields_edge** is the list with the name of key of the dict sent in the list of edges. The order must be the same in
the argument **fields** to stablish the correlation with the columns of the table.
----
-- Example -- 
```
edges_to_report = [{
    "detection_time": "01-01-2019",
    "serial_number": "TX124533",
    "enterprise": "Intelygenz",
    "links": "http://example1.es - http://example2.com - http://example3.net",
    "tickets": "No"
    }]

fields = ["Date of detection", "Serial Number", "Company", "LINKS", "Has ticket created?"]\
fields_edge = ["detection_time", "serial_number", "enterprise", "links", "tickets"]

_compose_email_object(edges_to_report, fields=fields, fields_edge=fields_edge)
```
----
This code generates a table like:


| Date of detection | Serial Number |   Company   |                                     LINKS                                    | Has ticket created? |
|:-----------------:|:-------------:|:-----------:|:----------------------------------------------------------------------------:|:-------------------:|
|     01-01-2019    |   TX124533  | Intelygenz | http://example1.es<br>http://example2.com<br>http://example3.net |          No         |