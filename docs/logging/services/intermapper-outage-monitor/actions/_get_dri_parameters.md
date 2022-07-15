## Get DRI parameters

[get_serial_attribute_from_inventory](../repositories/bruin_repository/get_serial_attribute_from_inventory.md)

* If response status for get serial attribute from inventory is not ok:
  ```python
  self._logger.warning(
      f"Bad status while getting inventory attributes' serial number for service number {service_number} "
      f"and client ID {client_id}. Skipping get DRI parameters..."
  )
  ```
  END

* If inventory attributes' `Serial Number` field is undefined:
  ```python
  self._logger.warning(
      f"No inventory attributes' found for service number {service_number} and client ID {client_id}. "
      "Skipping get DRI parameters..."
  )
  ```
  END

[get_dri_parameters](../repositories/dri_repository/get_dri_parameters.md)

* If response status for get DRI parameters is not ok:
  ```python
  self._logger.warning(
      f"Bad status while getting DRI parameters based on inventory attributes' serial number "
      f"{attributes_serial} for service number {service_number} and client ID {client_id}. "
      f"Skipping get DRI parameters..."
  )
  ```
  END