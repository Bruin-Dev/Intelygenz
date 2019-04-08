# Automatically generated by HonestCode
# Do not edit this file as it will be overwritten

Feature: Publish/receive msgs

  Scenario: Publish and receive from some topics
    Given an event bus
    When messages are published to the following topics
      | topic       | message   |
      | test.topic1 | message 1 |
      | test.topic2 | message 2 |
      | test.topic3 | message 3 |
    Then will receive all messages

  Scenario: Receive published message
    Given an event bus
    When a message is published
    Then will receive the message
