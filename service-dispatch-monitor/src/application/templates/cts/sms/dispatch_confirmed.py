CTS_SMS_DISPATCH_CONFIRMED = """This is an automated message from MetTel.

A dispatch has been confirmed for your location on {date_of_dispatch}.
"""


def cts_get_dispatch_confirmed_sms(body):
    return CTS_SMS_DISPATCH_CONFIRMED.format(
        date_of_dispatch=body.get('date_of_dispatch')
    )


CTS_SMS_DISPATCH_CONFIRMED_TECH = """This is an automated message from MetTel.

You have been confirmed for a dispatch on {date_of_dispatch}.
For {site} at {street}
"""


def cts_get_dispatch_confirmed_sms_tech(body):
    return CTS_SMS_DISPATCH_CONFIRMED_TECH.format(
        date_of_dispatch=body.get('date_of_dispatch'),
        site=body.get('site'),
        street=body.get('street')
    )


CTS_SMS_DISPATCH_TECH_12_HOURS_BEFORE_SMS = """This is an automated message from MetTel.

A field engineer will arrive in 12 hours, {date_of_dispatch}, at your location.

You will receive a text message at this number when they have arrived.
"""


def cts_get_tech_12_hours_before_sms(body):
    return CTS_SMS_DISPATCH_TECH_12_HOURS_BEFORE_SMS.format(
        date_of_dispatch=body.get('date_of_dispatch')
    )


CTS_SMS_DISPATCH_TECH_12_HOURS_BEFORE_SMS_TECH = """This is an automated message from MetTel.

You have a dispatch coming up in 12 hours, {date_of_dispatch}.
For {site} at {street}
"""


def cts_get_tech_12_hours_before_sms_tech(body):
    return CTS_SMS_DISPATCH_TECH_12_HOURS_BEFORE_SMS_TECH.format(
        date_of_dispatch=body.get('date_of_dispatch'),
        site=body.get('site'),
        street=body.get('street')
    )


CTS_SMS_DISPATCH_TECH_2_HOURS_BEFORE_SMS = """This is an automated message from MetTel.

A field engineer will arrive in 2 hours, {date_of_dispatch}, at your location.

You will receive a text message at this number when they have arrived.
"""


def cts_get_tech_2_hours_before_sms(body):
    return CTS_SMS_DISPATCH_TECH_2_HOURS_BEFORE_SMS.format(
        date_of_dispatch=body.get('date_of_dispatch')
    )


CTS_SMS_DISPATCH_TECH_2_HOURS_BEFORE_SMS_TECH = """This is an automated message from MetTel.

You have a dispatch coming up in 2 hours, {date_of_dispatch}.
For {site} at {street}
"""


def cts_get_tech_2_hours_before_sms_tech(body):
    return CTS_SMS_DISPATCH_TECH_2_HOURS_BEFORE_SMS_TECH.format(
        date_of_dispatch=body.get('date_of_dispatch'),
        site=body.get('site'),
        street=body.get('street')
    )
