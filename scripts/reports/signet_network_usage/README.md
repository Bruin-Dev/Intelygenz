# scripts

This folder contains some scripts used as tools for sending reports.

**Table of content:**

+ [Signet report](#signet_report)
    - [Description](#signet_report_description)
    - [Usage](#signet_report_usage)

## Signet report <a name="signet_report"></a>

### Description <a name="signet_report_description"></a>

The Python [script](signet_report.py). The script will create the csv report file in its folder, overwriting any existing `signet_report.csv` file.

### Usage <a name="signet_report_usage"></a>

Run this sequence of commands to initialize the Poetry virtualenv and install all required dependencies, including
`velocloud-bridge` source code, so it can be used as a Python package:

```shell
# These commands assume your current working dir is the root of the project
cd scripts/reports/signet_network_usage
poetry install
```

Next, run the script `installation_utils/environment_files_generator.py` but first edit the line to pull VeloCloud credentials
used in the production environment:
```python
VELOCLOUD_CREDENTIALS = parameters["pro"]["velocloud-bridge"]["velocloud-credentials"]
```

Run the following commands to source and export some environment variables required to use `velocloud-bridge` source code
as a library and connect to VeloCloud servers successfully:
```shell
set -a
source ../../../services/velocloud-bridge/src/config/env
set +a
```

Edit the following lines in the report script with the month you want to cover. The following setup will cover the month
of August:
```python
report_start_date = datetime(year=init_year, month=8, day=1, hour=0, minute=0, second=0, tzinfo=timezone.utc)
report_end_date = datetime(year=end_year, month=9, day=1, hour=0, minute=0, second=0, tzinfo=timezone.utc)
```

Finally, run the script with the following command:
```shell
poetry run python signet_report.py
```

After completion, the script should have generated a file named `signet_usage.csv` at `scripts/reports/signet_network_usage`.
You can send it to the customer as is.
