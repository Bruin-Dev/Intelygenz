# **ALGORITHM**
##### *OUTAGE_DETECTOR* (t = 10 min)
- 1\. Claim all the edges
- 2\. For each edge:
	- 2.1 Claim status
	- 2.2 Check status
		- If is OFFLINE, or any of it's links are DISCONNECTED, add a new QUARANTINE_JOB in APScheduler to check if the edge is still in outage situation after 10 minutes

##### *QUARANTINE_JOB* (t= 10 min)
- 1\. Check edge status:
	- 1.1. If the edge or any of the links is still in an outage condition and there is not any ticket for it add it to _EDGES_TO_REPORT_

##### *OUTAGE_REPORT* (t = ? min)
- 1\. Compose an email with all the edges from _EDGES_TO_REPORT_ at the moment of time defined
- 2\. Send the email
- 3\. Clear _EDGES_TO_REPORT_

#### Additional info
Stores of Redis:k
- _EDGES_TO_REPORT_