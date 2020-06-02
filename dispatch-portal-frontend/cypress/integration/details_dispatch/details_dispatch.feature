Feature: View dispatch details
  Enter in the dispatch portal and navigate to dispatch details

  Background: I login successfully
    Given I navigate to login page
    When I introduce valid credentials
    And I click to submit
    Then I navigate to Dashboard page

  Scenario: Click in logout button, then navigate to login page
    Given I on the DashboardPage
    When I click on an dispatchId row
    And I see the details of that dispatch
    Then I check info of dispatch
