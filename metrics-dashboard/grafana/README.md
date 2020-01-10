# Grafana

**Table of content:**

+ [Dashboard_generator](#dashboard_generator)
    - [Description](#dashboard_generator_description)
    - [Usage](#dashboard_generator_usage)

## Script dashboard_generator<a name="dashboard_generator"></a>

### Description <a name="dashboard_generator_description"></a>

[This script](./scripts/dashboard_generator.py) has been implemented in *Python* and it's used for the automatic generation of dashboards for some Mettel clients. It generates a folder for each provided company, creates a new dashboard with metrics for it and adds a new provider in the `dashboards/all.yaml` file to provisione it in Grafana.

### Usage <a name="dashboard_generator_usage"></a>

The script is automatically executed when a Docker image of Grafana is built.
