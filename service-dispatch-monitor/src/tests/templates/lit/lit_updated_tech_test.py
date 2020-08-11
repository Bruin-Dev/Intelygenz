from application.templates.lit.lit_updated_tech import lit_get_updated_tech_note

expected_updated_tech_note = """#*Automation Engine*# DIS37266
The Field Engineer assigned to this dispatch has changed.
Reference: 12345

Field Engineer
Michael J. Fox
+12123595129
"""


def lit_get_dispatch_requested_note_test():
    body = {
        'dispatch_number': 'DIS37266',
        'ticket_id': 12345,
        'tech_name': 'Michael J. Fox',
        'tech_phone': '+12123595129'
    }
    updated_tech_note = lit_get_updated_tech_note(body)

    assert updated_tech_note == expected_updated_tech_note
