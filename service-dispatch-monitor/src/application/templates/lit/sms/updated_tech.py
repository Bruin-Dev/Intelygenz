LIT_SMS_UPDATED_TECH = """This is an automated message from MetTel customer support.

The field engineer handling your dispatch on {date_of_dispatch} has changed.
The new field engineer will be: {tech_name}
"""


def lit_get_updated_tech_sms(body):
    return LIT_SMS_UPDATED_TECH.format(
        date_of_dispatch=body.get('date_of_dispatch'),
        tech_name=body.get('tech_name')
    )


LIT_SMS_UPDATED_TECH_TO_TECH = """This is an automated message from MetTel.

You have been confirmed for a dispatch on {date_of_dispatch}.
For {site} at {street}
"""


def lit_get_updated_tech_sms_tech(body):
    return LIT_SMS_UPDATED_TECH_TO_TECH.format(
        date_of_dispatch=body.get('date_of_dispatch'),
        site=body.get('site'),
        street=body.get('street')
    )
