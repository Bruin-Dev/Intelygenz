## Get site

[BruinClient::get_site](../../clients/bruin_client/get_site.md)

* If response is not ok:
  ```python
  self._logger.error(
      f"Got response with status {response['status']} while getting site information for params {params}."
  )
  ```
  END

* If site information is missing in response:
  ```python
  msg = f"No site information was found for site {params['site_id']} and client {params['client_id']}"
  self._logger.warning(msg)
  ```
  END 