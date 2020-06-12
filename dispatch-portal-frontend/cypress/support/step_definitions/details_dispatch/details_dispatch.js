import dataE2e from '../../../fixtures/config';
import { config } from '../../../../config/config';
// Scenario: Opening app [login feature]
// Scenario: I login successfully [login feature]

// Current Scenario: Click in logout button, then navigate to login page
// Given I on the DashboardPage ===> logout.feature

When('I click on an dispatchId row', function() {
  cy.get(`[data-test-id="dispatchId-${dataE2e.getDispatch.id}-link"]`).click();
});

And('I see the details of that dispatch', function() {
  cy.location().should(loc => {
    expect(loc.pathname).to.eq(`/dispatch/${dataE2e.getDispatch.id}`);
  });
});

Then('I check info of dispatch', function() {
  /* cy.get(`[data-test-id="dispatch-detail-slaLevel"]`).contains(dataE2e.getDispatch.slaLevel
  ); */
  cy.get(`[data-test-id="dispatch-detail-id"]`).contains(
    dataE2e.getDispatch.id
  );
  cy.get(`[data-test-id="dispatch-detail-dateDispatch"]`).contains(
    dataE2e.getDispatch.dispatch.date_of_dispatch
  );
  cy.get(`[data-test-id="dispatch-detail-timeDispatch"]`).contains(
    dataE2e.getDispatch.dispatch.time_of_dispatch
  );
  cy.get(`[data-test-id="dispatch-detail-timeZone"]`).contains(
    dataE2e.getDispatch.dispatch.time_zone
  );
  // cy.get(`[data-test-id="dispatch-detail"]`).contains(dataE2e.getDispatch.status)
  cy.get(`[data-test-id="dispatch-detail-requester-name"]`).contains(
    dataE2e.getDispatch.dispatch.name_of_mettel_requester
  );
  cy.get(`[data-test-id="dispatch-detail-requester-email"]`).contains(
    dataE2e.getDispatch.dispatch.mettel_requester_email
  );
  cy.get(`[data-test-id="dispatch-detail-requester-department"]`).contains(
    dataE2e.getDispatch.dispatch.mettel_department
  );
  /* cy.get(`[data-test-id="dispatch-detail-requester-phoneNumber"]`).contains(
    dataE2e.getDispatch.dispatch.mettel_department_phone_number
  ); */
  cy.get(`[data-test-id="dispatch-detail-onSiteContact-site"]`).contains(
    dataE2e.getDispatch.dispatch.job_site
  );
  cy.get(`[data-test-id="dispatch-detail-onSiteContact-street"]`).contains(
    dataE2e.getDispatch.dispatch.job_site_street
  );
  cy.get(`[data-test-id="dispatch-detail-onSiteContact-city"]`).contains(
    dataE2e.getDispatch.dispatch.job_site_city
  );
  cy.get(`[data-test-id="dispatch-detail-onSiteContact-state"]`).contains(
    dataE2e.getDispatch.dispatch.job_site_state
  );
  cy.get(`[data-test-id="dispatch-detail-onSiteContact-zip"]`).contains(
    dataE2e.getDispatch.dispatch.job_site_zip_code
  );
  cy.get(`[data-test-id="dispatch-detail-onSiteContact-phoneNumber"]`).contains(
    dataE2e.getDispatch.dispatch.job_site_contact_number
  );
  /* cy.get(`[data-test-id="dispatch-detail-details-serviceType"]`).contains(
    dataE2e.getDispatch.dispatch.scope_of_work
  ); */
  cy.get(`[data-test-id="dispatch-detail-details-instructions"]`).contains(
    dataE2e.getDispatch.dispatch.mettel_tech_call_in_instructions
  );
  cy.get(`[data-test-id="dispatch-detail-details-information"]`).contains(
    dataE2e.getDispatch.dispatch.scope_of_work
  );
  cy.get(`[data-test-id="dispatch-detail-details-materials"]`).contains(
    dataE2e.getDispatch.dispatch.materials_needed_for_dispatch
  );
  if (dataE2e.getDispatch.vendor === config.VENDORS.CTS) {
    cy.get(`[data-test-id="dispatch-detail-details-fieldEngineer"]`).contains(
      `${dataE2e.getDispatch.field_engineer_name} ${dataE2e.getDispatch.field_engineer_last_name}`
    );
    cy.get(
      `[data-test-id="dispatch-detail-details-fieldEngineerContactNumber"]`
    ).contains(dataE2e.getDispatch.dispatch.field_engineer_contact_number);
  }
});
