## Get billing data for a specific time frame

* While there are pages to fetch from the LuminAI API:
    ```python
    logger.info(
        "fetching billing data for {}".format(
            {"type": ",".join(billing_types), "start": str(start), "end": str(end), "start_token": start_token}
        )
    )
    ```

    [LuminClient::get_billing_data_for_period](../../clients/lumin_client/get_billing_data_for_period.md)