LIT_SMS_DISPATCH_CONFIRMED = """This is an automated message from MetTel.

A dispatch has been confirmed for your location on {date_of_dispatch}.
The field engineer handling this dispatch will be {tech_name}.
"""


def lit_get_dispatch_confirmed_sms(body):
    return LIT_SMS_DISPATCH_CONFIRMED.format(
        date_of_dispatch=body.get('date_of_dispatch'),
        tech_name=body.get('tech_name')
    )


LIT_SMS_DISPATCH_CONFIRMED_TECH = """This is an automated message from MetTel.

You have been confirmed for a dispatch on {date_of_dispatch}.
For {site} at {street}
"""


def lit_get_dispatch_confirmed_sms_tech(body):
    return LIT_SMS_DISPATCH_CONFIRMED_TECH.format(
        date_of_dispatch=body.get('date_of_dispatch'),
        site=body.get('site'),
        street=body.get('street')
    )


LIT_SMS_DISPATCH_TECH_X_HOURS_BEFORE_SMS = """This is an automated message from MetTel.

A field engineer will arrive in {hours} hours, {date_of_dispatch}, at your location.

You will receive a text message at this number when they have arrived.
"""


def lit_get_tech_x_hours_before_sms(body):
    return LIT_SMS_DISPATCH_TECH_X_HOURS_BEFORE_SMS.format(
        date_of_dispatch=body.get('date_of_dispatch'),
        hours=body.get('hours')

    )


LIT_SMS_DISPATCH_TECH_X_HOURS_BEFORE_SMS_TECH = """This is an automated message from MetTel.

You have a dispatch coming up in {hours} hours, {date_of_dispatch}.
For {site} at {street}
"""


def lit_get_tech_x_hours_before_sms_tech(body):
    return LIT_SMS_DISPATCH_TECH_X_HOURS_BEFORE_SMS_TECH.format(
        date_of_dispatch=body.get('date_of_dispatch'),
        site=body.get('site'),
        street=body.get('street'),
        hours=body.get('hours')

    )
