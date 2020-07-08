CTS_SMS_DISPATCH_TECH_ON_SITE = """This is an automated message from MetTel.
{field_engineer_name}, the field engineer handling today's repair has arrived on-site.
"""


def cts_get_tech_on_site_sms(body):
    return CTS_SMS_DISPATCH_TECH_ON_SITE.format(
        field_engineer_name=body.get('field_engineer_name')
    )
