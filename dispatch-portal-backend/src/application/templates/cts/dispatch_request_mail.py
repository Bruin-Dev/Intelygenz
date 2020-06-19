CTS_DISPATCH_REQUEST_MAIL = """
<hr style="width:100%;text-align:left;margin-left:0">
<h1>[TEST] CTS - MetTel Service Submission Portal</h1>
<hr style="width:100%;text-align:left;margin-left:0">
<p>Onsite Time Needed: {onsite_time_needed}</p>
<p>Onsite Timezone: {timezone_of_dispatch}</p>
<p>Reference: {reference}</p>
<p>SLA Level: {sla_level}</p>
<p>Location Country: {location_country}</p>
<p>Location: {location_owner}</p>
<p>{city}, {state} {zip}</p>
<p>Location ID: {location_address_1} {location_address_2}</p>
<p>Location Owner: {location_owner}</p>
<p>Onsite Contact: {onsite_contact_name} {onsite_contact_lastname}</p>
<p>Contact #: {onsite_contact_phone_number}</p>
<p>Failure Experienced: {failure_experienced}</p>
<p>Onsite SOW: {onsite_sow}</p>
<p>Materials Needed:</p>
<p>{materials_needed}</p>
<p>Service Category: {service_category}</p>
<p>Name: {name} {lastname}</p>
<p>Phone: {phone_number}</p>
<p>Email: {email}</p>
"""


def render_email_template(payload):
    return CTS_DISPATCH_REQUEST_MAIL.format(
        onsite_time_needed=payload.get('onsite_time_needed', ''),
        timezone_of_dispatch=payload.get('timezone_of_dispatch', ''),
        reference=payload.get('reference', ''),
        sla_level=payload.get('sla_level', ''),
        location_country=payload.get('location_country', ''),
        location_owner=payload.get('location_owner', ''),
        city=payload.get('city', ''),
        state=payload.get('state', ''),
        zip=payload.get('zip', ''),
        location_address_1=payload.get('location_address_1', ''),
        location_address_2=payload.get('location_address_2', ''),
        onsite_contact_name=payload.get('onsite_contact_name', ''),
        onsite_contact_lastname=payload.get('onsite_contact_lastname', ''),
        onsite_contact_phone_number=payload.get('onsite_contact_phone_number', ''),
        failure_experienced=payload.get('failure_experienced', ''),
        onsite_sow=payload.get('onsite_sow', ''),
        materials_needed=payload.get('materials_needed', ''),
        service_category=payload.get('service_category', ''),
        name=payload.get('name', ''),
        lastname=payload.get('lastname', ''),
        phone_number=payload.get('phone_number', ''),
        email=payload.get('email', '')
    )
