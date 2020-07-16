import dataE2e from '../../../fixtures/config';
// Scenario: Opening app [login feature]
// Scenario: I login successfully [login feature]

// Current Scenario: Go to new dispatch form and created it
Given('I navigate to new dispatch', function() {
  cy.visit('/new-dispatch');
});

When('I introduce valid fields for new dispatch', function() {
  cy.get('input[name=dateDispatch]').type(dataE2e.dispatch.date_of_dispatch);
  cy.get('select[name=timeDispatch]').select(dataE2e.dispatch.time_of_dispatch);
  cy.get('select[name=timeZone]').select(dataE2e.dispatch.time_zone);
  cy.get(
    `input[type="radio"][name=vendor][value=${dataE2e.dispatch.vendor}]`
  ).check();
  cy.get('input[name=mettelId]').type(dataE2e.dispatch.mettel_bruin_ticket_id);
  cy.get('input[name=owner]').type(dataE2e.dispatch.job_site);
  cy.get('input[name=address1]').type(dataE2e.dispatch.job_site_street);
  cy.get('input[name=address2]').type(dataE2e.dispatch.job_site_street2);
  cy.get('input[name=city]').type(dataE2e.dispatch.job_site_city);
  cy.get('select[name=state]').select(dataE2e.dispatch.job_site_state);
  cy.get('input[name=zip]').type(dataE2e.dispatch.job_site_zip_code);
  cy.get('input[name=firstName]').type(dataE2e.dispatch.job_site_contact_name);
  cy.get('input[name=lastName]').type(
    dataE2e.dispatch.job_site_contact_lastname
  );
  cy.get('input[name=phoneNumber]').type(
    dataE2e.dispatch.job_site_contact_number
  );
  cy.get('textarea[name=issues]').type(dataE2e.dispatch.scope_of_work);
  cy.get('textarea[name=materials]').type(
    dataE2e.dispatch.materials_needed_for_dispatch
  );
  cy.get('textarea[name=instructions]').type(
    dataE2e.dispatch.mettel_tech_call_in_instructions
  );
  cy.get('input[name=firstNameRequester]').type(
    dataE2e.dispatch.name_of_mettel_requester
  );
  cy.get('input[name=lastNameRequester]').type(
    dataE2e.dispatch.last_name_of_mettel_requester
  );
  cy.get('select[name=department]').select(dataE2e.dispatch.mettel_department);
  cy.get('select[name=phoneNumberRequester]').select(
    dataE2e.dispatch.mettel_requester_phone_number
  );

  cy.get('input[name=emailRequester]').type(
    dataE2e.dispatch.mettel_requester_email
  );
});

And('I click to submit new dispatch', function() {
  cy.get('[data-test-id="new-dispatch-submit"]').click();
});

// Then ==> I navigate to Dashboard page
