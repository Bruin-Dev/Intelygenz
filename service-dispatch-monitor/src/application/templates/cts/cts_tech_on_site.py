CTS_TECH_ON_SITE = """#*Automation Engine*# {dispatch_number}
Dispatch Management - Field Engineer On Site
SMS notification sent to {phone}

The field engineer, {field_engineer_name} has arrived.
"""


def cts_get_tech_on_site_note(body):
    return CTS_TECH_ON_SITE.format(
        dispatch_number=body.get('dispatch_number'),
        field_engineer_name=body.get('field_engineer_name'),
        phone=body.get('phone')
    )
