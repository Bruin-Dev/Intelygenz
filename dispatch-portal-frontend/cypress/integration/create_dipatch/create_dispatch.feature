Feature: Create dispatch
  Create new dispatch and view your details

  Background: I login successfully
    Given I navigate to login page
    When I introduce valid credentials
    And I click to submit
    Then I navigate to Dashboard page

  Scenario: Go to new dispatch form and created it
    Given I navigate to new dispatch
    When I introduce valid fields for new dispatch
    And I click to submit new dispatch
    Then I navigate to Dashboard page

  Scenario: Go to new dispatch form and check if get location button is disabled
    Given I navigate to new dispatch
    When I introduce valid field for ticket id
    And I delete the ticket id itself
    Then The button should be disabled

  Scenario: Go to new dispatch form and get location details by ticket id
    Given I navigate to new dispatch
    When I introduce valid field for ticket id
    And I click to the get location button
    Then The location form should be filled
