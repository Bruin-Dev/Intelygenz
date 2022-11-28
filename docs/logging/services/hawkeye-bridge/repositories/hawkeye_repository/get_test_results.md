## Get test results

Call [__make_paginated_request](__make_paginated_request.md) with
[HawkeyeClient::get_tests_results](../../clients/hawkeye_client/get_tests_results.md) to fetch all
available pages for the desired set of filters.

* For each pair of probe UID:
    * For each test result associated to the probe UID:

        [HawkeyeClient::get_test_result_details](../../clients/hawkeye_client/get_test_result_details.md)

        * If something fail when trying to get the details for the test result:
          ```python
          logger.error(f"Error when calling get_tests_result_details using test result ID {test_result_id})")
          ```
          _Continue to next test result_