import config from '../../../fixtures/config';

// Scenario: I login Unsuccessfull with invalid mail

// Given => 'I navigate to login page'
When('I leave the fields empty', function() {
  cy.get('input[name=email]').clear();
  cy.get('input[name=password]').clear();
});
// When => 'I click to submit'
Then('I receive a validation error', function() {
  cy.get('[data-test-id="error-email-login-form"]').should('exist');
  cy.get('[data-test-id="error-password-login-form"]').should('exist');
});

When('I introduce invalid fields', function() {
  cy.get('input[name=email]').type(config.userEmail);
  cy.get('input[name=password]').type('01234');
});
// When => 'I click to submit'
Then('I receive api error', function() {
  cy.get('[data-test-id="error-api-login-form"]').should('exist');
});
