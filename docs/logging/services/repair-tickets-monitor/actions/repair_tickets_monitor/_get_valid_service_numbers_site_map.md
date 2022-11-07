## Get valid service numbers site map

* for potential_service_number in potential_service_numbers
    result = [BruinRepository:verify_service_number_information](../../repositories/bruin_repository/verify_service_number_information.md)
    * if result["status"] is not 200 or 404
      Raise `ResponseException`
      ```python
      (f"Exception while verifying service_number: {potential_service_number}")
      ```