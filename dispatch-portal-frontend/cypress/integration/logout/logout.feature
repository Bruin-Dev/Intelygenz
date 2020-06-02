Feature: Log out
  Enter in the dispatch portal and then log out

  Background: I login successfully
    Given I navigate to login page
    When I introduce valid credentials
    And I click to submit
    Then I navigate to Dashboard page

  Scenario: Click in logout button, then navigate to login page
    Given I on the DashboardPage
    When I click in logout button
    Then I navigate to LoginPage
