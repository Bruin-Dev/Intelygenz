LIT_DISPATCH_CONFIRMED = """#*Automation Engine*#
Dispatch Management - Dispatch Confirmed
Dispatch scheduled for {date_of_dispatch} @ {time_of_dispatch} {time_zone}

Field Engineer
{tech_name}
{tech_phone}
"""


def lit_get_dispatch_confirmed_note(body):
    return LIT_DISPATCH_CONFIRMED.format(
        date_of_dispatch=body.get('date_of_dispatch'),
        time_of_dispatch=body.get('time_of_dispatch'),
        time_zone=body.get('time_zone'),
        tech_name=body.get('tech_name'),
        tech_phone=body.get('tech_phone')
    )


LIT_DISPATCH_CONFIRMED_SMS = """#*Automation Engine*#
Dispatch confirmation SMS sent to {phone_number}
"""


def lit_get_dispatch_confirmed_sms_note(body):
    return LIT_DISPATCH_CONFIRMED_SMS.format(
        phone_number=body.get('phone_number')
    )


LIT_TECH_24_HOURS_BEFORE_SMS_NOTE = """#*Automation Engine*#
Dispatch 24h prior reminder SMS sent to {phone_number}
"""


def lit_get_tech_24_hours_before_sms_note(body):
    return LIT_TECH_24_HOURS_BEFORE_SMS_NOTE.format(
        phone_number=body.get('phone_number')
    )


LIT_TECH_2_HOURS_BEFORE_SMS_NOTE = """#*Automation Engine*#
Dispatch 2h prior reminder SMS sent to {phone_number}
"""


def lit_get_tech_2_hours_before_sms_note(body):
    return LIT_TECH_2_HOURS_BEFORE_SMS_NOTE.format(
        phone_number=body.get('phone_number')
    )
