import json
import yaml
import os
import re


COMPANY_LIST = ['Titan America|85940|']


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

        print(f'Creating dashboard for company {company_name}')
        d = build_new_dashboard(dashboard, c, id)

        folder_path = os.path.join(dashboards_path, company_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        print(f'Saving dashboard to folder {folder_path}')
        file_name = os.path.join(dashboards_path, company_name,
                                 f'{company_name}-dashboard.json')
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

        print(f'Adding provider to .yaml file')
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

        id += 1


if __name__ == "__main__":
    main()
