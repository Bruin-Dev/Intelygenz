# scripts

This folder contains some scripts used as tools for sending reports.

**Table of content:**

+ [Signet report](#signet_report)
    - [Description](#signet_report_description)
    - [Usage](#signet_report_usage)

## Signet report <a name="signet_report"></a>

### Description <a name="signet_report_description"></a>

The Python [script](./signet_report.py). The script will create the csv report file in its folder, overwriting any existing `signet_report.csv` file.

### Usage <a name="signet_report_usage"></a>

First thing you need to do is copying the script to the velocloud bridge source folder so the dependencies can be solved.

Edit the following lines in the file with the month you want to cover, in this example is august:
```python
report_start_date = datetime(year=init_year, month=8, day=1, hour=0, minute=0, second=0, tzinfo=timezone.utc)
report_end_date = datetime(year=end_year, month=9, day=1, hour=0, minute=0, second=0, tzinfo=timezone.utc)
```

Run the script `environment_files_generator.py` but first edit the line:
```python
VELOCLOUD_CREDENTIALS = parameters["pro"]["velocloud-bridge"]["velocloud-credentials"]
```

The env file will be generated in the path `services/velocloud-bridge/src/config/env`, there you will need to edit the line
with the velocloud credentials adding commas this way VELOCLOUD_CREDENTIALS="EXAMPLE"

Now go to ~/.bashrc and add the following lines at the end of the file pointing to the source folder you have the project:
```bash
alias papertrailvars="export PAPERTRAIL_ACTIVE=false PAPERTRAIL_HOST=logs.papertrailapp.com PAPERTRAIL_PORT=1111"
alias velovars="cd ~/code/automation-engine/services/velocloud-bridge/src/config && source ./env && export NATS_SERVER1 REDIS_HOSTNAME VELOCLOUD_CREDENTIALS TIMEZONE ENVIRONMENT_NAME && cd -"
```

Once you have this alias run the following commands
```bash
source ~/.bashrc
papertrailvars
velovars
```

After doing this go to the `signet_report.py` folder and run the script with:
```
$ poetry install
$ python3 signet_report.py
```
