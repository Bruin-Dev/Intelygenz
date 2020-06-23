from application.mappers import cts_mapper
from application.templates.cts.dispatch_request_mail import render_email_template

expected_dispatch_request_mail = """
<hr style="width:100%;text-align:left;margin-left:0">
<h1>[TEST] CTS - MetTel Service Submission Portal</h1>
<hr style="width:100%;text-align:left;margin-left:0">
<p>Onsite Time Needed: 2019-11-14 6PM-8PM</p>
<p>Onsite Timezone: Pacific Time</p>
<p>Reference: 123456</p>
<p>SLA Level: Pre-planned</p>
<p>Location Country: United States</p>
<p>Location: Red Rose Inn</p>
<p>Pleasantown, CA 99088</p>
<p>Location ID: 123 Fake Street 123 Fake Street</p>
<p>Location Owner: Red Rose Inn</p>
<p>Onsite Contact: Jane Doe</p>
<p>Contact #: +1 666 6666 666</p>
<p>Failure Experienced: Device is bouncing constantly</p>
<p>Onsite SOW: When arriving to the site call HOLMDEL NOC for telematic assistance</p>
<p>Materials Needed:</p>
<p>Laptop, cable, tuner, ladder,internet hotspot</p>
<p>Service Category: Troubleshooting</p>
<p>Name: Karen Doe</p>
<p>Phone: +1 666 6666 666</p>
<p>Email: karen.doe@mettel.net</p>
"""


def get_dispatch_request_mail_test(new_dispatch):
    cts_body_mapped = cts_mapper.map_create_dispatch(new_dispatch)
    dispatch_request_mail = render_email_template(cts_body_mapped)
    assert dispatch_request_mail == expected_dispatch_request_mail
