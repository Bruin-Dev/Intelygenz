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