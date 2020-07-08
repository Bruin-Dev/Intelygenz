from application.templates.lit.lit_tech_on_site import lit_get_tech_on_site_note

expected_tech_on_site_note_note = """#*Automation Engine*# DIS37266
Dispatch Management - Field Engineer On Site
SMS notification sent to +12123595129

The field engineer, Michael J. Fox has arrived.
"""


def lit_get_dispatch_requested_note_test():
    body = {
        'dispatch_number': 'DIS37266',
        'field_engineer_name': 'Michael J. Fox',
        'phone': '+12123595129'
    }
    tech_on_site_note = lit_get_tech_on_site_note(body)

    assert tech_on_site_note == expected_tech_on_site_note_note
