//    Scenario: Check that the option to back to the Home Page appears
When('I click on back arrow button', function() {
  cy.get('general-header > .toolbar > .back-button').click();
});

Then('I navigate to LoggedHome page', function() {
  cy.get('welcome-header').should('exist');
});
