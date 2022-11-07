## Create tickets

* for site_id, service_numbers in site_id_sn_buckets.items()
    * try 
      result = _upsert_outage_ticket_rpc()
    * catch `RpcError`
        ```python
        log.exception(
                    "email_id=%s Error while creating ticket for %s and client %s",
                    email.id,
                    service_numbers,
                    email.client_id,
                )
        ```
    * if result.status is equal to UpsertedStatus.created
        ```python
         log.info("email_id=%s Successfully created outage ticket %s", email.id, result.ticket_id)
        ```
    * else result.status is equal to UpsertedStatus.updated
        ```python
        log.info("email_id=%s Ticket already present", email.id)
        ```
    [_post_process_upsert](_post_process_upsert.md)
    * if email.is_reply_email
        [_post_process_upsert](_post_process_upsert.md)
    * try _subscribe_user_rpc
    * catch `RpcError`
        ```python
        log.exception(f"email_id={email.id} Error while subscribing user to ticket {result.ticket_id}")
        ```