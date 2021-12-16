import asyncio
import re

from collections import defaultdict
from datetime import datetime
from datetime import timedelta

import aiohttp


# Misc
resource_id_url_rgx = re.compile(r'\/[1-9]\d+')

# Metrics lookup config
usage_metric = 'bruin_api_usage_total'
lookup_start = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

prometheus_host = 'localhost'
prometheus_port = 9090
prometheus_endpoint = '/api/v1/series'
prometheus_url = f'http://{prometheus_host}:{prometheus_port}{prometheus_endpoint}'

queryparams = {
    'match[]': usage_metric,
    'start': lookup_start,
}

# Panels dimensions and coordinates
panels_per_row = 2

height = 7
width = 12
x_offset = 12
y_offset = 7


def get_panel_template():
    return {
        "aliasColors": {},
        "dashLength": 10,
        "fieldConfig": {
            "defaults": {
                "custom": {},
                "links": []
            },
            "overrides": []
        },
        "fill": 1,
        "gridPos": {},  # Intentionally blank, needs to be filled dynamically
        "id": 0,  # Intentionally blank, needs to be filled dynamically
        "legend": {
            "avg": False,
            "current": False,
            "max": False,
            "min": False,
            "show": True,
            "total": False,
            "values": False
        },
        "lines": True,
        "linewidth": 1,
        "maxPerRow": 2,
        "NonePointMode": "None",
        "options": {
            "alertThreshold": True
        },
        "pluginVersion": "7.4.1",
        "pointradius": 2,
        "renderer": "flot",
        "repeatDirection": "h",
        "seriesOverrides": [],
        "spaceLength": 10,
        "targets": [],  # Intentionally blank, needs to be filled dynamically
        "thresholds": [],
        "timeRegions": [],
        "title": "",  # Intentionally blank, needs to be filled dynamically
        "tooltip": {
            "shared": True,
            "sort": 0,
            "value_type": "individual"
        },
        "type": "graph",
        "xaxis": {
            "buckets": None,
            "mode": "time",
            "name": None,
            "show": True,
            "values": []
        },
        "yaxes": [
            {
              "decimals": 0,
              "format": "short",
              "label": None,
              "logBase": 1,
              "max": None,
              "min": None,
              "show": True,
              "$$hashKey": "object:110"
            },
            {
              "format": "short",
              "label": None,
              "logBase": 1,
              "max": None,
              "min": None,
              "show": True,
              "$$hashKey": "object:111"
            }
        ],
        "yaxis": {
            "align": False,
            "alignLevel": None
        },
        "bars": False,
        "dashes": False,
        "description": "",
        "fillGradient": 0,
        "hiddenSeries": False,
        "percentage": False,
        "points": False,
        "stack": False,
        "steppedLine": False,
        "timeFrom": None,
        "timeShift": None,
        "datasource": None
    }


def get_pods_target(method, endpoint, endpoint_has_resource_id=False):
    if endpoint_has_resource_id:
        endpoint = get_endpoint_labelvalue_for_multiple_resource_ids(endpoint)
        expression = f"sum({usage_metric}{{method=\"{method}\", endpoint_=~\"{endpoint}\", namespace=~\"$namespace\"}}) by (pod)"
    else:
        expression = f"{usage_metric}{{method=\"{method}\", endpoint_=\"{endpoint}\", namespace=~\"$namespace\"}}"

    return {
        "expr": expression,
        "interval": "",
        "legendFormat": "Pod {{pod}}",
        "refId": "API usage per pod"
    }


def get_totals_target(method, endpoint):
    return {
        "expr": f"sum({usage_metric}{{method=\"{method}\", endpoint_=\"{endpoint}\", namespace=~\"$namespace\"}})",
        "interval": "",
        "legendFormat": "Total",
        "refId": "Total API usage"
    }


def get_panel_title(method, endpoint, endpoint_has_resource_id=False):
    if endpoint_has_resource_id:
        endpoint = get_endpoint_without_resource_ids(endpoint)

    return f'{method.upper()} {endpoint}'


def has_resource_id(endpoint):
    return bool(resource_id_url_rgx.search(endpoint))


def get_endpoint_without_resource_ids(endpoint):
    return resource_id_url_rgx.sub('/<id>', endpoint)


def get_endpoint_labelvalue_for_multiple_resource_ids(endpoint):
    return resource_id_url_rgx.sub('/[1-9][0-9]*', endpoint)


def get_grid_position(panels_count):
    if panels_count == 0:
        return {
            "h": height,
            "w": width,
            "x": 0,
            "y": 0,
        }

    free_cells_in_last_row = panels_count % panels_per_row
    can_add_panel_to_row = free_cells_in_last_row > 0

    target_row_number = panels_count // panels_per_row

    if can_add_panel_to_row:
        x = (panels_per_row - free_cells_in_last_row) * x_offset
        y = target_row_number * y_offset
    else:
        x = 0
        y = target_row_number * y_offset

    return {
        "h": height,
        "w": width,
        "x": x,
        "y": y,
    }


async def generate_dashboard():
    async with aiohttp.ClientSession() as c:
        async with c.get(prometheus_url, params=queryparams) as r:
            samples = await r.json()

    # Group endpoints by HTTP method
    endpoints_by_http_method = defaultdict(set)
    for s in samples['data']:
        endpoints_by_http_method[s['method']].add(s['endpoint'])

    # Generate panels for the dashboard
    dashboard_panels = []
    for http_method, endpoints in endpoints_by_http_method.items():
        for e in endpoints:
            panel = get_panel_template()
            totals_target = get_totals_target(http_method, e)

            resource_id_in_endpoint = has_resource_id(e)
            title = get_panel_title(http_method, e, endpoint_has_resource_id=resource_id_in_endpoint)
            pods_target = get_pods_target(http_method, e, endpoint_has_resource_id=resource_id_in_endpoint)

            panel['id'] = len(dashboard_panels) + 1
            panel['title'] = title
            panel['targets'] = [
                pods_target,
                totals_target,
            ]
            panel['gridPos'] = get_grid_position(panels_count=len(dashboard_panels))
            dashboard_panels.append(panel)

    import json
    print(json.dumps(dashboard_panels, indent=4))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate_dashboard())
    loop.close()
