from application.templates.cts.dispatch_cancel_mail import render_cancel_email_template

expected_cancel_dispatch_request_mail = """
<hr style="width:100%;text-align:left;margin-left:0">
<h1>CTS - MetTel Service Submission Portal</h1>
<hr style="width:100%;text-align:left;margin-left:0">
<p>Please cancel this dispatch.<p>
<p>CTS ticket S-12345.</p>
"""


def get_dispatch_cancel_request_mail_test():
    body = {
        'dispatch_number': 'S-12345'
    }
    dispatch_cancel_request_mail = render_cancel_email_template(body)
    assert dispatch_cancel_request_mail == expected_cancel_dispatch_request_mail
