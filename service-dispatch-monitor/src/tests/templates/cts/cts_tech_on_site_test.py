from application.templates.cts.cts_tech_on_site import cts_get_tech_on_site_note

expected_tech_on_site_note_note = """#*Automation Engine*#
Dispatch Management - Field Engineer On Site

Michael J. Fox has arrived
"""


def cts_get_dispatch_requested_note_test():
    body = {
      'field_engineer_name': 'Michael J. Fox'
    }
    tech_on_site_note = cts_get_tech_on_site_note(body)

    assert tech_on_site_note == expected_tech_on_site_note_note
