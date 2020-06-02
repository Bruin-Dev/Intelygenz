// Scenario: Opening app [login feature]
// Scenario: I login successfully [login feature]

// Current Scenario: Click in logout button, then navigate to login page
Given('I on the DashboardPage', function() {
  cy.location().should(loc => {
    expect(loc.pathname).to.eq('/');
  });
});

When('I click in logout button', function() {
  cy.get('[data-test-id="logout-button"]').click();
});

Then('I navigate to LoginPage', function() {
  cy.location().should(loc => {
    expect(loc.pathname).to.eq('/login');
  });
});
