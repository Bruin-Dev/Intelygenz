LIT_TECH_ON_SITE = """#*Automation Engine*#
Dispatch Management - Field Engineer On Site

{field_engineer_name} has arrived
"""


def lit_get_tech_on_site_note(body):
    return LIT_TECH_ON_SITE.format(
        field_engineer_name=body.get('field_engineer_name')
    )
