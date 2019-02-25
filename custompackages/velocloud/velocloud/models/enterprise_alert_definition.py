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


class EnterpriseAlertDefinition(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, isSystemOnly=None, isOperatorOnly=None):
        """
        EnterpriseAlertDefinition - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'isSystemOnly': 'bool',
            'isOperatorOnly': 'bool'
        }

        self.attribute_map = {
            'isSystemOnly': 'isSystemOnly',
            'isOperatorOnly': 'isOperatorOnly'
        }

        self._isSystemOnly = isSystemOnly
        self._isOperatorOnly = isOperatorOnly

    @property
    def isSystemOnly(self):
        """
        Gets the isSystemOnly of this EnterpriseAlertDefinition.

        :return: The isSystemOnly of this EnterpriseAlertDefinition.
        :rtype: bool
        """
        return self._isSystemOnly

    @isSystemOnly.setter
    def isSystemOnly(self, isSystemOnly):
        """
        Sets the isSystemOnly of this EnterpriseAlertDefinition.

        :param isSystemOnly: The isSystemOnly of this EnterpriseAlertDefinition.
        :type: bool
        """

        self._isSystemOnly = isSystemOnly

    @property
    def isOperatorOnly(self):
        """
        Gets the isOperatorOnly of this EnterpriseAlertDefinition.

        :return: The isOperatorOnly of this EnterpriseAlertDefinition.
        :rtype: bool
        """
        return self._isOperatorOnly

    @isOperatorOnly.setter
    def isOperatorOnly(self, isOperatorOnly):
        """
        Sets the isOperatorOnly of this EnterpriseAlertDefinition.

        :param isOperatorOnly: The isOperatorOnly of this EnterpriseAlertDefinition.
        :type: bool
        """

        self._isOperatorOnly = isOperatorOnly

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
        if not isinstance(other, EnterpriseAlertDefinition):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
