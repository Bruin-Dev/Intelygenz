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


class EdgeQOSDataServiceRateLimit(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, enabled=None, inputType=None, value=None):
        """
        EdgeQOSDataServiceRateLimit - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'enabled': 'bool',
            'inputType': 'str',
            'value': 'int'
        }

        self.attribute_map = {
            'enabled': 'enabled',
            'inputType': 'inputType',
            'value': 'value'
        }

        self._enabled = enabled
        self._inputType = inputType
        self._value = value

    @property
    def enabled(self):
        """
        Gets the enabled of this EdgeQOSDataServiceRateLimit.

        :return: The enabled of this EdgeQOSDataServiceRateLimit.
        :rtype: bool
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        """
        Sets the enabled of this EdgeQOSDataServiceRateLimit.

        :param enabled: The enabled of this EdgeQOSDataServiceRateLimit.
        :type: bool
        """

        self._enabled = enabled

    @property
    def inputType(self):
        """
        Gets the inputType of this EdgeQOSDataServiceRateLimit.

        :return: The inputType of this EdgeQOSDataServiceRateLimit.
        :rtype: str
        """
        return self._inputType

    @inputType.setter
    def inputType(self, inputType):
        """
        Sets the inputType of this EdgeQOSDataServiceRateLimit.

        :param inputType: The inputType of this EdgeQOSDataServiceRateLimit.
        :type: str
        """

        self._inputType = inputType

    @property
    def value(self):
        """
        Gets the value of this EdgeQOSDataServiceRateLimit.

        :return: The value of this EdgeQOSDataServiceRateLimit.
        :rtype: int
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Sets the value of this EdgeQOSDataServiceRateLimit.

        :param value: The value of this EdgeQOSDataServiceRateLimit.
        :type: int
        """

        self._value = value

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
        if not isinstance(other, EdgeQOSDataServiceRateLimit):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
