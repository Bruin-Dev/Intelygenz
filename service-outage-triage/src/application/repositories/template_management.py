import jinja2
from collections import OrderedDict
import re
from shortuuid import uuid
from datetime import datetime, timedelta
import base64


class TemplateRenderer:
    def __init__(self, _service_id, _config):
        self._config = _config
        self._service_id = _service_id

    def _ticket_object_to_email_obj(self, ticket_dict, **kwargs):
        template_vars = {}
        template = "src/templates/{}".format(kwargs.get("template", "service_outage_triage.html"))
        logo = "src/templates/images/{}".format(kwargs.get("logo", "logo.png"))
        header = "src/templates/images/{}".format(kwargs.get("header", "header.jpg"))
        templateLoader = jinja2.FileSystemLoader(searchpath=".")
        templateEnv = jinja2.Environment(loader=templateLoader)
        templ = templateEnv.get_template(template)
        template_vars["__EDGE_COUNT__"] = '1'
        template_vars["__SERIAL_NUMBER__"] = "VC05200028729"
        overview_keys = ["Orchestrator instance", "Edge Name", "Edge URL", "QoE URL", "Transport URL", "Edge Status",
                         "Interface LABELMARK1", "Label LABELMARK2", "Interface GE1 Status", "Interface LABELMARK3",
                         "Interface GE2 Status", "Label LABELMARK4"]
        events_keys = ["Company Events URL", "Last Edge Online", "Last Edge Offline", "Last GE1 Interface Online",
                       "Last GE1 Interface Offline", "Last GE2 Interface Online", "Last GE2 Interface Offline"]
        edge_overview = OrderedDict()
        edge_events = OrderedDict()
        for key, value in ticket_dict.items():
            if key in overview_keys:
                edge_overview[key] = value
            if key in events_keys:
                edge_events[key] = value
        rows = []
        for idx, key in enumerate(edge_overview.keys()):
            parsed_key = re.sub(r" LABELMARK(.)*", "", key)
            rows.append({
                "type": "even" if idx % 2 == 0 else "row",
                "__KEY__": parsed_key,
                "__VALUE__": str(edge_overview[key])
            })
        template_vars["__OVERVIEW_ROWS__"] = rows
        rows = []
        for idx, key in enumerate(edge_events.keys()):
            rows.append({
                "type": "even" if idx % 2 == 0 else "row",
                "__KEY__": key,
                "__VALUE__": str(edge_events[key])
            })
        template_vars["__EVENT_ROWS__"] = rows
        email_html = templ.render(**template_vars)
        return {
                'request_id': uuid(),
                'response_topic': f"notification.email.response.{self._service_id}",
                'email_data': {
                    'subject': f'Service outage triage ({datetime.now().strftime("%Y-%m-%d")})',
                    'recipient': self._config.TRIAGE_CONFIG["recipient"],
                    'text': 'this is the accessible text for the email',
                    'html': email_html,
                    'images': [
                        {
                            'name': 'logo',
                            'data': base64.b64encode(open(logo, 'rb').read()).decode('utf-8')
                        },
                        {
                            'name': 'header',
                            'data': base64.b64encode(open(header, 'rb')
                                                     .read()).decode('utf-8')
                        },
                    ],
                    'attachments': []
                }
            }
