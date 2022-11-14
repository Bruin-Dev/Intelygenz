## Get network enterprises for Triage

* For each VCO under monitoring:

    [get_network_enterprises](get_network_enterprises.md)

    * If response status for get network enterprises is not ok:
      ```python
      logger.error(f"Error while retrieving network enterprises for VeloCloud host {host}: {response}")
      ```
      _Continue with next VCO_