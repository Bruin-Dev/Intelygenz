Feature: Login
  Login with the correct credentials

Scenario: I login successfully
  Given I navigate to login page
  When I introduce valid credentials
  And I click to submit
  Then I navigate to Dashboard page
