LIT_TECH_ON_SITE = """#*MetTel's IPA*# {dispatch_number}
Dispatch Management - Field Engineer On Site
SMS notification sent to {phone}

The field engineer, {field_engineer_name} has arrived.
"""


def lit_get_tech_on_site_note(body):
    return LIT_TECH_ON_SITE.format(
        dispatch_number=body.get('dispatch_number'),
        field_engineer_name=body.get('field_engineer_name'),
        phone=body.get('phone')
    )
