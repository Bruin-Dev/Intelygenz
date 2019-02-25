# coding: utf-8

"""
    Velocloud API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: 3.2.19
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class FirewallInboundRule(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, name=None, match=None, action=None, ruleLogicalId=None):
        """
        FirewallInboundRule - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'name': 'str',
            'match': 'FirewallRuleMatch',
            'action': 'FirewallInboundRuleAction',
            'ruleLogicalId': 'str'
        }

        self.attribute_map = {
            'name': 'name',
            'match': 'match',
            'action': 'action',
            'ruleLogicalId': 'ruleLogicalId'
        }

        self._name = name
        self._match = match
        self._action = action
        self._ruleLogicalId = ruleLogicalId

    @property
    def name(self):
        """
        Gets the name of this FirewallInboundRule.

        :return: The name of this FirewallInboundRule.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this FirewallInboundRule.

        :param name: The name of this FirewallInboundRule.
        :type: str
        """

        self._name = name

    @property
    def match(self):
        """
        Gets the match of this FirewallInboundRule.

        :return: The match of this FirewallInboundRule.
        :rtype: FirewallRuleMatch
        """
        return self._match

    @match.setter
    def match(self, match):
        """
        Sets the match of this FirewallInboundRule.

        :param match: The match of this FirewallInboundRule.
        :type: FirewallRuleMatch
        """

        self._match = match

    @property
    def action(self):
        """
        Gets the action of this FirewallInboundRule.

        :return: The action of this FirewallInboundRule.
        :rtype: FirewallInboundRuleAction
        """
        return self._action

    @action.setter
    def action(self, action):
        """
        Sets the action of this FirewallInboundRule.

        :param action: The action of this FirewallInboundRule.
        :type: FirewallInboundRuleAction
        """

        self._action = action

    @property
    def ruleLogicalId(self):
        """
        Gets the ruleLogicalId of this FirewallInboundRule.

        :return: The ruleLogicalId of this FirewallInboundRule.
        :rtype: str
        """
        return self._ruleLogicalId

    @ruleLogicalId.setter
    def ruleLogicalId(self, ruleLogicalId):
        """
        Sets the ruleLogicalId of this FirewallInboundRule.

        :param ruleLogicalId: The ruleLogicalId of this FirewallInboundRule.
        :type: str
        """

        self._ruleLogicalId = ruleLogicalId

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, FirewallInboundRule):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
