## Get tickets

* for ticket_id in tickets_id
    bruin_bridge_response = [BruinRepository:get_single_ticket_basic_info](../../repositories/bruin_repository/get_single_ticket_basic_info.md)
    * if bruin_bridge_response["status"] == 200
        * try and remove dash from In-Progress and In-Review status
        * catch `ValueError`
            ```python
            log.warning(
                        "email_id=%s Unknown ticket status, response=%s, error=%s", email_id, bruin_bridge_response, e
                    )
            ```