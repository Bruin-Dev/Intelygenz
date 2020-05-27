import config from '../../../fixtures/config';

// Scenario: Opening app
Given('I open app', function() {
  cy.visit('/login');
  cy.clearCookies();
});

// Scenario: I login successfully
Given('I navigate to login page', function() {
  cy.visit('/login');
  cy.clearCookies();
  cy.location().should(loc => {
    expect(loc.pathname).to.eq('/login');
  });
});

When('I introduce valid credentials', function() {
  cy.get('input[name=email]').type(config.userEmail);
  cy.get('input[name=password]').type(config.userPassword);
});

When('I click to submit', function() {
  cy.get('[data-test-id="login-submit"]').click();
});

Then('I navigate to Dashboard page', function() {
  cy.location().should(loc => {
    expect(loc.pathname).to.eq('/');
  });
});
