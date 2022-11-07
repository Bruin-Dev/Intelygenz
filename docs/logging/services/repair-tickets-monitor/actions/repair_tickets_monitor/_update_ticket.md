# Update ticket

* try _append_note_to_ticket_rpc

* catch `RpcError`
    ```python
    log.error("email_id=%s append_note_to_ticket_rpc(%s, %s) => %s", email.id, ticket.id, note, e)
    ```

[BruinRepository:link_email_to_ticket](../../repositories/bruin_repository/link_email_to_ticket.md)
