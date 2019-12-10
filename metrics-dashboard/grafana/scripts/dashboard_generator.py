import json
import yaml
import os
import re

# llamada a velocloud; cogemos enterprise_name (mockeado)
COMPANY_LIST = ['Titan America|85940|']


def get_new_panels(panels):

    # First step - removing Edges processed panel
    panels = [p for p in panels if p["id"] != 8]

    # Second step - modifying queries. This is obviously not ideal
    # but is safer than just using a regex. All queries have one of the
    # following formats:
    # sum by (whatever) ((edge_state_gauge))
    # sum by (whatever) ((edge_state_gauge{state='CONNECTED'}))
    # Which should become:
    # sum by (whatever) ((edge_state_gauge{enterprise_name='$enterprise'}))
    # sum by (whatever)
    # ((edge_state_gauge{state='CONNECTED', enterprise_name='$enterprise'}))
    for p in panels:
        for t in p["targets"]:
            if "_gauge))" in t["expr"]:
                q = re.split(re.escape("_gauge"), t["expr"])
                t["expr"] = f"{q[0]}{{enterprise_name='$enterprise'}}{q[1]}"
            elif "}))" in t["expr"]:
                q = re.split(re.escape("}))"), t["expr"])
                t["expr"] = f"{q[0]}, enterprise_name='$enterprise'{q[1]}"
            else:
                raise("Unknown query")

    return panels


def get_new_templating(templating, company):

    new_var = {
        "current": {
          "text": company,
          "value": company
        },
        "hide": 2,
        "label": "",
        "name": "enterprise",
        "options": [
          {
            "selected": True,
            "text": company,
            "value": company
          }
        ],
        "query": company,
        "skipUrlSync": False,
        "type": "constant"
    }

    templating["list"].append(new_var)
    return templating


def get_company_name(company):
    return company.split('|')[0]


def get_company_id(company):
    return company.split('|')[1]


def build_new_dashboard(dummy, company, id):
    return {
        "annotations": dummy["annotations"],
        "editable": dummy["editable"],
        "gnetId": dummy["gnetId"],
        "graphTooltip": dummy["graphTooltip"],
        "id": id,
        "iteration": dummy["iteration"],
        "links": dummy["links"],
        "panels": dummy["panels"],
        "refresh": dummy["refresh"],
        "schemaVersion": dummy["schemaVersion"],
        "style": dummy["style"],
        "tags": dummy["tags"],
        "templating": get_new_templating(dummy["templating"], company),
        "time": dummy["time"],
        "timepicker": dummy["timepicker"],
        "timezone": dummy["timezone"],
        "title": f'{get_company_name(company)} Dashboard',
        "version": dummy["version"]
    }


def main():
    main_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    dashboards_path = os.path.join(main_path, 'dashboards-definitions')
    parent_dashboard_path = os.path.join(dashboards_path,
                                         'dummy', 'dummy.json')

    with open(parent_dashboard_path, 'r') as f:
        dashboard = json.load(f)

    id = dashboard["id"] + 1
    for c in COMPANY_LIST:
        company_name = get_company_name(c).replace(' ', '-').lower()

        # Creating the new dashboard
        d = build_new_dashboard(dashboard, c, id)

        # Creating a new folder under dashboards-definitions
        # if it does not exist yet
        folder_path = os.path.join(dashboards_path, company_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Storing the dashboard in the folder
        file_name = os.path.join(dashboards_path, company_name,
                                 f'{company_name}-dashboard.json')
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

        # Adding new provider in yaml file if it does not exist yet
        # Note that maximum uid length is 40 as per the grafana docs
        yaml_path = os.path.join(main_path, 'dashboards', 'all.yml')
        new_provider = {
            "name": f'{company_name}-dashboard',
            "org_id": 1,
            "folder": company_name,
            "type": 'file',
            "options": {"path": f'/var/lib/grafana/dashboards/{company_name}'}
        }

        with open(yaml_path, 'r') as f:
            y = yaml.safe_load(f)
            if f'{company_name}-dashboard' not in [p["name"] for p in y["providers"]]:
                y["providers"].append(new_provider)
        with open(yaml_path, 'w') as f:
            yaml.dump(y, f)

        # Increasing id by one
        id += 1


if __name__ == "__main__":
    main()