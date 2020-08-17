from application.templates.lit.sms.tech_on_site import lit_get_tech_on_site_sms

expected_tech_on_site_sms = """This is an automated message from MetTel.
Michael Jordan, the field engineer handling today's repair has arrived on-site.
"""


def lit_get_tech_on_site_sms_test():
    body = {
        'field_engineer_name': 'Michael Jordan'
    }
    tech_on_site_sms_sms = lit_get_tech_on_site_sms(body)

    assert tech_on_site_sms_sms == expected_tech_on_site_sms
