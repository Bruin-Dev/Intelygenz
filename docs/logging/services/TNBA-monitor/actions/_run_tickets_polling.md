## Run tickets polling
```
self._logger.info("Starting TNBA process...")
```
* [get_cache_for_tnba_monitoring](../repositories/customer_cache/get_cache_for_tnba_monitoring.md)
* If get cache status is not Ok:
  ```
  self._logger.warning(f"Bad status calling to get cache. Skipping run ticket polling ...")
  ```
* [get_edges_for_tnba_monitoring](../repositories/velocloud_repository/get_edges_for_tnba_monitoring.md)
* If not edges statuses:
  ```
  self._logger.error("No edges statuses were received from VeloCloud. Aborting TNBA monitoring...")
  ```
```
self._logger.info("Keeping serials that exist in both the customer cache and the set of edges statuses...")
```
* [get_links_metrics_for_autoresolve](get_links_metrics_for_autoresolve.md)
* If not link metrics:
  ```
  self._logger.info("List of links metrics arrived empty. Skipping...")
  ```
* [get_events_by_serial_and_interface](../repositories/velocloud_repository/get_events_by_serial_and_interface.md)
```
self._logger.info("Loading customer cache and edges statuses by serial into the monitor instance...")
self._logger.info("Getting all open tickets for all customers...")
```
* [_get_all_open_tickets_with_details_for_monitored_companies](_get_all_open_tickets_with_details_for_monitored_companies.md)
```
self._logger.info(
            f"Got {len(open_tickets)} open tickets for all customers. "
            f"Filtering them (and their details) to get only the ones under the device list"
        )
```
* [_filter_tickets_and_details_related_to_edges_under_monitoring](_filter_tickets_and_details_related_to_edges_under_monitoring.md)
```
self._logger.info(
            f"Got {len(relevant_open_tickets)} relevant tickets for all customers. "
            f"Cleaning them up to exclude all invalid notes..."
        )
self._logger.info("Getting T7 predictions for all relevant open tickets...")
```
* [_get_predictions_by_ticket_id](_get_predictions_by_ticket_id.md)
```
self._logger.info("Removing erroneous T7 predictions...")
```
* [_remove_erroneous_predictions](_remove_erroneous_predictions.md)
```
self._logger.info("Creating detail objects based on all tickets...")
self._logger.info("Discarding resolved ticket details...")
self._logger.info("Discarding ticket details of outage tickets whose last outage happened too recently...")
```
* [_filter_outage_ticket_details_based_on_last_outage](_filter_outage_ticket_details_based_on_last_outage.md)
```
self._logger.info("Mapping all ticket details with their predictions...")
```
* [_map_ticket_details_with_predictions](_map_ticket_details_with_predictions.md)
```
self._logger.info(
            f"{len(ticket_detail_objects)} ticket details were successfully mapped to predictions. "
            "Processing all details..."
        )
```
* [_process_ticket_detail](_process_ticket_detail.md)
```
self._logger.info("All ticket details were processed.")
```
* If not append notes TNBA:
  ```
  self._logger.info("No TNBA notes for append were built for any detail processed.")
  ```
* Else:
  ```
  self._logger.info(f"{len(self._tnba_notes_to_append)} TNBA notes were built for append.")
  ```
  * [_append_tnba_notes](_append_tnba_notes.md)
```
self._logger.info(f"TNBA process finished! Took {round((end_time - start_time) / 60, 2)} minutes.")
```