CTS_DISPATCH_CANCEL_MAIL = """
<hr style="width:100%;text-align:left;margin-left:0">
<h1>CTS - MetTel Service Submission Portal</h1>
<hr style="width:100%;text-align:left;margin-left:0">
<p>Please cancel this dispatch.<p>
<p>CTS ticket {dispatch_number}.</p>
"""


def render_cancel_email_template(payload):
    return CTS_DISPATCH_CANCEL_MAIL.format(
        dispatch_number=payload.get('dispatch_number', '')
    )
