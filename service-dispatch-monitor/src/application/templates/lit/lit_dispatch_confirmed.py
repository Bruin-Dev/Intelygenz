LIT_DISPATCH_CONFIRMED = """#*MetTel's IPA*# {dispatch_number}
Dispatch Management - Dispatch Confirmed
Dispatch scheduled for {date_of_dispatch} @ {time_of_dispatch} {time_zone}
"""


def lit_get_dispatch_confirmed_note(body):
    return LIT_DISPATCH_CONFIRMED.format(
        dispatch_number=body.get('dispatch_number'),
        date_of_dispatch=body.get('date_of_dispatch'),
        time_of_dispatch=body.get('time_of_dispatch'),
        time_zone=body.get('time_zone'),
    )


LIT_FIELD_ENGINEER_CONFIRMED = """#*MetTel's IPA*# {dispatch_number}
Dispatch Management - Field Engineer Confirmed

Field Engineer
{tech_name}
{tech_phone}
"""


def lit_get_field_engineer_confirmed_note(body):
    return LIT_FIELD_ENGINEER_CONFIRMED.format(
        dispatch_number=body.get('dispatch_number'),
        tech_name=body.get('tech_name'),
        tech_phone=body.get('tech_phone')
    )


LIT_DISPATCH_CONFIRMED_SMS = """#*MetTel's IPA*# {dispatch_number}
Dispatch confirmation SMS sent to {phone_number}
"""


def lit_get_dispatch_confirmed_sms_note(body):
    return LIT_DISPATCH_CONFIRMED_SMS.format(
        dispatch_number=body.get('dispatch_number'),
        phone_number=body.get('phone_number'),
    )


LIT_DISPATCH_CONFIRMED_SMS_TECH = """#*MetTel's IPA*# {dispatch_number}
Dispatch confirmation SMS tech sent to {phone_number}
"""


def lit_get_dispatch_confirmed_sms_tech_note(body):
    return LIT_DISPATCH_CONFIRMED_SMS_TECH.format(
        dispatch_number=body.get('dispatch_number'),
        phone_number=body.get('phone_number'),
    )


LIT_TECH_X_HOURS_BEFORE_SMS_NOTE = """#*MetTel's IPA*# {dispatch_number}
Dispatch {hours}h prior reminder SMS sent to {phone_number}
"""


def lit_get_tech_x_hours_before_sms_note(body):
    return LIT_TECH_X_HOURS_BEFORE_SMS_NOTE.format(
        dispatch_number=body.get('dispatch_number'),
        phone_number=body.get('phone_number'),
        hours=body.get('hours')

    )


LIT_TECH_X_HOURS_BEFORE_SMS_TECH_NOTE = """#*MetTel's IPA*# {dispatch_number}
Dispatch {hours}h prior reminder tech SMS sent to {phone_number}
"""


def lit_get_tech_x_hours_before_sms_tech_note(body):
    return LIT_TECH_X_HOURS_BEFORE_SMS_TECH_NOTE.format(
        dispatch_number=body.get('dispatch_number'),
        phone_number=body.get('phone_number'),
        hours=body.get('hours')
    )
