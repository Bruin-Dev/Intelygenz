## Run tickets polling
```
self._logger.info(f"Starting triage process...")
```
* [get_cache_for_triage_monitoring](../../repositories/customer_cache_repository/get_cache_for_triage_monitoring.md)
```
self._logger.info("Getting all open tickets for all customers...")
```
* [_get_all_open_tickets_with_details_for_monitored_companies](_get_all_open_tickets_with_details_for_monitored_companies.md)
```
self._logger.info(
            f"Got all {len(open_tickets)} open tickets for all customers. "
            f"Filtering them to get only the ones under the device list"
        )
```
* [_filter_tickets_and_details_related_to_edges_under_monitoring](_filter_tickets_and_details_related_to_edges_under_monitoring.md)
```
self._logger.info(
            f"Got {len(relevant_open_tickets)} relevant tickets for all customers. "
            f"Cleaning them up to exclude all invalid notes..."
        )
```
* [_filter_irrelevant_notes_in_tickets](_filter_irrelevant_notes_in_tickets.md)
```
self._logger.info(f"Splitting relevant tickets in tickets with and without triage...")
```
* [_get_ticket_details_with_and_without_triage](_get_ticket_details_with_and_without_triage.md)
```
self._logger.info(
            f"Ticket details split successfully. "
            f"Ticket details with triage: {len(details_with_triage)}. "
            f"Ticket details without triage: {len(details_without_triage)}. "
            "Processing both sets..."
        )
```
* [_build_edges_status_by_serial](_build_edges_status_by_serial.md)
* [_process_ticket_details_with_triage](_process_ticket_details_with_triage.md)
```
self._logger.info(f"Triage process finished! took {time.time() - total_start_time} seconds")
```