# Table of contents
  * [Description](#description)
  * [Work Flow](#work-flow)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The `digi-reboot-report` service creates a report every day of the last full day based on the DiGi recovery logs, 
and then emails it out.
# Work Flow
The DiGi reboot report is called every 24 hours, and starts off by getting all the DiGi recovery logs from the past 3 days.
It then takes all the ticket IDs from those logs and makes a list. From the list we get all the ticket task histories
one by one. 

Using the function `_parse_ticket_history` we parse through the task histories to create a dict similar to this:
```angular2html
{
            'outage_type': 'Unclassified',
            'reboot_attempted': False,
            'reboot_time': None,
            'process_attempted': False,
            'process_successful': False,
            'process_start': None,
            'process_end': None,
            'process_length': None,
            'reboot_method': None,
            'autoresolved': False,
            'autoresolve_time': None,
            'autoresolve_correlation': False,
            'autoresolve_diff': None,
            'forwarded': False
}
```

Once we have a ticket parsed into this format, we check if `reboot_attempted` is True and the `.date()` of the `reboot_time`
matches the previous day. If it satisfies both of those condition it is added to the ticket map. Which is mapped by `ticket_id` to ticket task history dict.
The two conditions ensures that every value in the ticket map has attempted a DiGi reboot, and the dates in the ticket map are only that of the previous day
or the last full day.

After that we take all the recovery logs data and fill in the other values of each dictionary in the ticket map respectively based
on matching ticket ids. 

Last step is take all the data from the ticket map to create a csv file that then is sent out through email.
# Capabilities used
- [DiGi bridge](../digi-bridge/README.md)
- [Bruin bridge](../bruin-bridge/README.md)
- [Notifier](../notifier/README.md)

# Running in docker-compose 

`docker-compose up --build nats-server redis digi-bridge bruin-bridge notifier digi-reboot-report`
