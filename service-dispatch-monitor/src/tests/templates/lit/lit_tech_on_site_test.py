from application.templates.lit.lit_tech_on_site import lit_get_tech_on_site_note

expected_tech_on_site_note_note = """#*Automation Engine*#
Dispatch Management - Field Engineer On Site

Michael J. Fox has arrived
"""


def get_dispatch_requested_note_test():
    body = {
      'field_engineer_name': 'Michael J. Fox'
    }
    tech_on_site_note = lit_get_tech_on_site_note(body)

    assert tech_on_site_note == expected_tech_on_site_note_note
