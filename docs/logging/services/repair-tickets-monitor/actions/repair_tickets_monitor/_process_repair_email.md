## Process repair email

```python
log.info("email_id=%s Running Repair Email Process", email.id)
```

inference_data = [_get_inference](_get_inference.md)

* if no inference_data
  ```python
  log.error("email_id=%s No inference data. Marking email as complete in Redis", email.id)
  ```
  [NewTaggedEmailsRepository:mark_complete](../../repositories/new_tagged_emails_repository/mark_complete.md)

```python
log.info(
                "email_id=%s inference: potential services numbers=%s potential_tickets_numbers=%s",
                email.id,
                potential_service_numbers,
                potential_ticket_numbers,
            )
```

[_get_tickets](_get_tickets.md)

* try
  [_get_valid_service_numbers_site_map](_get_valid_service_numbers_site_map.md)
  log.info("email_id=%s service_numbers_site_map=%s", email.id, service_number_site_map)
  * for service_number, site_id in service_number_site_map
    * try to get asset topics rpc
    * catch `RpcError`
      ```python
      log.warning(
                   f"[email_id={email.id}] _process_repair_email():get_topics_device_rpc({asset_id}): {e}"
                 )
      ```
  ```python
  log.info("email_id=%s allowed_service_numbers_site_map=%s", email.id, allowed_service_number_site_map)
  ```
  [_get_existing_tickets](_get_existing_tickets.md)
  ```python
  log.info("email_id=%s existing_tickets=%s", email.id, existing_tickets)
  ```
* catch `ResponseException`
  ```python
  log.error("email_id=%s Error in bruin %s, could not process email", email.id, e)
  ```
  [_save_output](_save_output.md)
  [NewTaggedEmailsRepository:mark_complete](../../repositories/new_tagged_emails_repository/mark_complete.md)

```python
log.info(
                "email_id=%s Found %s sites with previous cancellations",
                email.id,
                len(site_ids_with_previous_cancellations),
            )

log.info(
                "email_id=%s map_with_cancellations=%s map_without_cancellations=%s",
                email.id,
                map_with_cancellations,
                map_without_cancellations,
            )

log.info(
                "email_id=%s is_actionable=%s predicted_class=%s",
                email.id,
                is_actionable,
                inference_data.get("predicted_class"),
            )
```

* if is_actionable
  [_create_tickets](_create_tickets.md)


* if not allowed_service_number_site_map
  * if is_ticket_actionable
    * for ticket in operable_tickets
      [_update_ticket](_update_ticket.md)

* if not service_number_site_map and not output.tickets_updated and not output.tickets_could_be_updated 
  ```python
  log.info(f"email_id={email.id} No service number nor ticket actions triggered")
  
  log.info(f"email_id={email.id} auto_reply_enabled={auto_reply_enabled}")
  
  log.info(f"email_id={email.id} auto_reply_allowed={auto_reply_allowed}")
  ```
  * if email.is_parent_email and is_actionable and not output.validated_tickets and send_auto_reply
    ```python
    log.info(f"email_id={email.id} Sending auto-reply")
    ```
  * else email.is_reply_email
    ```python
    log.info(f"email_id={email.id} Restoring parent_email {email.parent.id}")
    ```
  ```python
  log.info("email_id=%s output_send_to_save=%s", email.id, output)
  ```
  [_save_output](_save_output.md)


* if tickets_automated and no_tickets_failed and not feedback_not_created_due_cancellations
  ```python
  log.info("email_id=%s Calling bruin to mark email as done", email.id)
  ```
  [BruinRepository:mark_email_as_done](../../repositories/bruin_repository/mark_email_as_done.md)
  * if email.is_reply_email
    [BruinRepository:mark_email_as_done](../../repositories/bruin_repository/mark_email_as_done.md)
  
```python
log.info("email_id=%s Removing email from Redis", email.id)
```
[NewTaggedEmailsRepository:mark_complete](../../repositories/new_tagged_emails_repository/mark_complete.md)