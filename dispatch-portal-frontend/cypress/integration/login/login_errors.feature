Feature: Login errors
  Login errors

  Scenario: I login Unsuccessfull with errors
    Given I navigate to login page

    # Test input password/email required
    When I leave the fields empty
    And I click to submit
    Then I receive a validation error

    # Test api validation with error
    When I introduce invalid fields
    And I click to submit
    Then I receive api error


