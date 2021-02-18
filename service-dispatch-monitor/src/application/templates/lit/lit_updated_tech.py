LIT_UPDATED_TECH = """#*MetTel's IPA*# {dispatch_number}
The Field Engineer assigned to this dispatch has changed.
Reference: {ticket_id}

Field Engineer
{tech_name}
{tech_phone}
"""


def lit_get_updated_tech_note(body):
    return LIT_UPDATED_TECH.format(
        dispatch_number=body.get('dispatch_number'),
        ticket_id=body.get('ticket_id'),
        tech_name=body.get('tech_name'),
        tech_phone=body.get('tech_phone')
    )
