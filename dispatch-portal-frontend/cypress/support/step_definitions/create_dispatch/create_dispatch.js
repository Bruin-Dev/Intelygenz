import config from '../../../fixtures/config';
// Scenario: Opening app [login feature]
// Scenario: I login successfully [login feature]

// Current Scenario: Go to new dispatch form and created it
Given('I navigate to new dispatch', function() {
  cy.visit('/new-dispatch');
});

When('I introduce valid fields for new dispatch', function() {
  cy.get('input[name=dateDispatch]').type(config.dispatch.date_of_dispatch);
  cy.get('select[name=timeDispatch]').select(config.dispatch.time_of_dispatch);
  cy.get('select[name=timeZone]').select(config.dispatch.time_zone);
  cy.get(
    `input[type="checkbox"][name=vendor][value=${config.dispatch.vendor}]`
  ).check();
  cy.get('input[name=mettelId]').type(config.dispatch.mettel_bruin_ticket_id);
  cy.get('input[name=owner]').type(config.dispatch.job_site);
  cy.get('input[name=address1]').type(config.dispatch.job_site_street);
  cy.get('input[name=address2]').type(config.dispatch.job_site_street2);
  cy.get('input[name=city]').type(config.dispatch.job_site_city);
  cy.get('select[name=state]').select(config.dispatch.job_site_state);
  cy.get('input[name=zip]').type(config.dispatch.job_site_zip_code);
  cy.get('input[name=firstName]').type(config.dispatch.job_site_contact_name);
  cy.get('input[name=lastName]').type(
    config.dispatch.job_site_contact_lastname
  );
  cy.get('input[name=phoneNumber]').type(
    config.dispatch.job_site_contact_number
  );
  cy.get('textarea[name=issues]').type(config.dispatch.scope_of_work);
  cy.get('textarea[name=materials]').type(
    config.dispatch.materials_needed_for_dispatch
  );
  cy.get('textarea[name=instructions]').type(
    config.dispatch.mettel_tech_call_in_instructions
  );
  cy.get('input[name=firstNameRequester]').type(
    config.dispatch.name_of_mettel_requester
  );
  cy.get('input[name=lastNameRequester]').type(
    config.dispatch.last_name_of_mettel_requester
  );
  cy.get('select[name=department]').select(config.dispatch.mettel_department);
  cy.get('input[name=phoneNumberRequester]').type(
    config.dispatch.mettel_requester_phone_number
  );
  cy.get('input[name=emailRequester]').type(
    config.dispatch.mettel_requester_email
  );
});

And('I click to submit new dispatch', function() {
  cy.get('[data-test-id="new-dispatch-submit"]').click();
});

Then('I navigate to Dispatch detail page', function() {
  cy.location().should(loc => {
    expect(loc.pathname).to.eq(`/dispatch/${config.dispatch.id}`);
  });
});
