## Run Lumin Billing Report job

```python
logger.info("Starting DiGi reboot report process")
logger.info("Grabbing DiGi recovery logs")
```

* The DiGi reboot report is called every 24 hours, and starts off by getting all the DiGi recovery logs from the past 3 days.
It then takes all the ticket IDs from those logs and makes a list. From the list we get all the ticket task histories
one by one. 

[DiGiRebootReport::get_digi_recovery_logs](../repositories/digi_repository/get_digi_recovery_logs.md)

[_get_all_ticket_ids_from_digi_recovery_logs](_get_all_ticket_ids_from_digi_recovery_logs.md)

[_get_ticket_task_histories](_get_ticket_task_histories.md)

[_merge_recovery_logs](_merge_recovery_logs.md)

* Last step is take all the data from the ticket map to create a csv file that then is sent out through email.

[_generate_and_email_csv_file](_generate_and_email_csv_file.md)

```python
logger.info(f"DiGi reboot report process finished in {round((stop - start) / 60, 2)} minutes")
```
