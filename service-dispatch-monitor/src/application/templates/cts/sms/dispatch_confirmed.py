CTS_SMS_DISPATCH_CONFIRMED = """This is an automated message from MetTel customer support.

A dispatch has been confirmed for your location on {date_of_dispatch}.
"""


def cts_get_dispatch_confirmed_sms(body):
    return CTS_SMS_DISPATCH_CONFIRMED.format(
        date_of_dispatch=body.get('date_of_dispatch')
    )


CTS_SMS_DISPATCH_TECH_24_HOURS_BEFORE_SMS = """This is an automated message from MetTel customer support.

A field engineer will arrive in 24 hours, {date_of_dispatch}, at your location.

You will receive a text message at this number when they have arrived.
"""


def cts_get_tech_24_hours_before_sms(body):
    return CTS_SMS_DISPATCH_TECH_24_HOURS_BEFORE_SMS.format(
        date_of_dispatch=body.get('date_of_dispatch')
    )


CTS_SMS_DISPATCH_TECH_2_HOURS_BEFORE_SMS = """This is an automated message from MetTel customer support.

A field engineer will arrive in 2 hours, {date_of_dispatch}, at your location.

You will receive a text message at this number when they have arrived.
"""


def cts_get_tech_2_hours_before_sms(body):
    return CTS_SMS_DISPATCH_TECH_2_HOURS_BEFORE_SMS.format(
        date_of_dispatch=body.get('date_of_dispatch')
    )
