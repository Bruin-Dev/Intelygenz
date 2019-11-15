# **ALGORITHM**
##### *OUTAGE_DETECTOR* (t = 10 min)
- 1\. Claim all the edges
- 2\. For each edge:
	- 2.1. Claim status
	- 2.2. Check status
		- 2.2.1. If is online, add in _EDGES_ONLINE_ (gives a TTL ensures stores don’t stay corrupted after reboot of some service)
		- 2.2.2. If is offline, add in _EDGES_QUARANTINE_ (give a TTL)

##### *OUTAGE_OBSERVER* (t= 5 min)
- 1\. Remove edges from quarantine (_EDGES_QUARANTINE_) and edges which have to be reported (_EDGES_TO_REPORT_) those are again online (_EDGES_ONLINE_)
- 2\. Empty _EDGES_ONLINE_
- 3\. For each edge in _EDGES_QUARANTINE_:
	- 3.1. Check how many time has taken from quarantine
		- 3.1.1. If the time is higher than 40 minutos (check this time ) AND TOO it hasn’t got a opened ticket from outage, extract the edge from _EDGES_QUARANTINE_ and add it to _EDGES_TO_REPORT_

##### *OUTAGE_REPORT* (t = ? min)
- 1\. Compose an email with all the edges from _EDGES_TO_REPORT_ at the moment of time defined
- 2\. Send the email
- 3\. empty _EDGES_TO_REPORT_

#### Additional info
Stores of Redis:
- _EDGES_QUARANTINE_
- _EDGES_ONLINE_
- _EDGES_TO_REPORT_