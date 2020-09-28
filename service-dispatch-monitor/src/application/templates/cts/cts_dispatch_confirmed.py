CTS_DISPATCH_CONFIRMED = """#*Automation Engine*# {dispatch_number}
Dispatch Management - Dispatch Confirmed
Dispatch scheduled for {date_of_dispatch}

Field Engineer
{tech_name}
{tech_phone}
"""


def cts_get_dispatch_confirmed_note(body):
    return CTS_DISPATCH_CONFIRMED.format(
        dispatch_number=body.get('dispatch_number'),
        date_of_dispatch=body.get('date_of_dispatch'),
        tech_name=body.get('tech_name'),
        tech_phone=body.get('tech_phone')
    )


CTS_DISPATCH_CONFIRMED_SMS = """#*Automation Engine*# {dispatch_number}
Dispatch confirmation SMS sent to {phone_number}
"""


def cts_get_dispatch_confirmed_sms_note(body):
    return CTS_DISPATCH_CONFIRMED_SMS.format(
        dispatch_number=body.get('dispatch_number'),
        phone_number=body.get('phone_number')
    )


CTS_DISPATCH_CONFIRMED_SMS_TECH = """#*Automation Engine*# {dispatch_number}
Dispatch confirmation SMS tech sent to {phone_number}
"""


def cts_get_dispatch_confirmed_sms_tech_note(body):
    return CTS_DISPATCH_CONFIRMED_SMS_TECH.format(
        dispatch_number=body.get('dispatch_number'),
        phone_number=body.get('phone_number')
    )


CTS_TECH_X_HOURS_BEFORE_SMS_NOTE = """#*Automation Engine*# {dispatch_number}
Dispatch {hours}h prior reminder SMS sent to {phone_number}
"""


def cts_get_tech_x_hours_before_sms_note(body):
    return CTS_TECH_X_HOURS_BEFORE_SMS_NOTE.format(
        dispatch_number=body.get('dispatch_number'),
        phone_number=body.get('phone_number'),
        hours=body.get('hours')
    )


CTS_TECH_X_HOURS_BEFORE_SMS_TECH_NOTE = """#*Automation Engine*# {dispatch_number}
Dispatch {hours}h prior reminder tech SMS sent to {phone_number}
"""


def cts_get_tech_x_hours_before_sms_tech_note(body):
    return CTS_TECH_X_HOURS_BEFORE_SMS_TECH_NOTE.format(
        dispatch_number=body.get('dispatch_number'),
        phone_number=body.get('phone_number'),
        hours=body.get('hours')
    )
