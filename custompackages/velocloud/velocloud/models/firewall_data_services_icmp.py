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


class FirewallDataServicesIcmp(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, enabled=None, allowSelectedIp=None, ruleLogicalId=None):
        """
        FirewallDataServicesIcmp - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'enabled': 'bool',
            'allowSelectedIp': 'list[str]',
            'ruleLogicalId': 'str'
        }

        self.attribute_map = {
            'enabled': 'enabled',
            'allowSelectedIp': 'allowSelectedIp',
            'ruleLogicalId': 'ruleLogicalId'
        }

        self._enabled = enabled
        self._allowSelectedIp = allowSelectedIp
        self._ruleLogicalId = ruleLogicalId

    @property
    def enabled(self):
        """
        Gets the enabled of this FirewallDataServicesIcmp.

        :return: The enabled of this FirewallDataServicesIcmp.
        :rtype: bool
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        """
        Sets the enabled of this FirewallDataServicesIcmp.

        :param enabled: The enabled of this FirewallDataServicesIcmp.
        :type: bool
        """

        self._enabled = enabled

    @property
    def allowSelectedIp(self):
        """
        Gets the allowSelectedIp of this FirewallDataServicesIcmp.
        List of IP addresses allowed ICMP access

        :return: The allowSelectedIp of this FirewallDataServicesIcmp.
        :rtype: list[str]
        """
        return self._allowSelectedIp

    @allowSelectedIp.setter
    def allowSelectedIp(self, allowSelectedIp):
        """
        Sets the allowSelectedIp of this FirewallDataServicesIcmp.
        List of IP addresses allowed ICMP access

        :param allowSelectedIp: The allowSelectedIp of this FirewallDataServicesIcmp.
        :type: list[str]
        """

        self._allowSelectedIp = allowSelectedIp

    @property
    def ruleLogicalId(self):
        """
        Gets the ruleLogicalId of this FirewallDataServicesIcmp.

        :return: The ruleLogicalId of this FirewallDataServicesIcmp.
        :rtype: str
        """
        return self._ruleLogicalId

    @ruleLogicalId.setter
    def ruleLogicalId(self, ruleLogicalId):
        """
        Sets the ruleLogicalId of this FirewallDataServicesIcmp.

        :param ruleLogicalId: The ruleLogicalId of this FirewallDataServicesIcmp.
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
        if not isinstance(other, FirewallDataServicesIcmp):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
