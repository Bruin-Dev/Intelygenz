# Automatically generated by HonestCode
# Do not edit this file as it will be overwritten

Feature: Publish/receive msgs

  Scenario: Receive published message
    Given an event bus
    When a message is published
    Then will receive the message
