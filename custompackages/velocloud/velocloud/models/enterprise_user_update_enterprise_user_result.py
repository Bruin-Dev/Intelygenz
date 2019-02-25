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


class EnterpriseUserUpdateEnterpriseUserResult(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, error=None, rows=None):
        """
        EnterpriseUserUpdateEnterpriseUserResult - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'error': 'str',
            'rows': 'int'
        }

        self.attribute_map = {
            'error': 'error',
            'rows': 'rows'
        }

        self._error = error
        self._rows = rows

    @property
    def error(self):
        """
        Gets the error of this EnterpriseUserUpdateEnterpriseUserResult.
        An error message explaining why the method failed

        :return: The error of this EnterpriseUserUpdateEnterpriseUserResult.
        :rtype: str
        """
        return self._error

    @error.setter
    def error(self, error):
        """
        Sets the error of this EnterpriseUserUpdateEnterpriseUserResult.
        An error message explaining why the method failed

        :param error: The error of this EnterpriseUserUpdateEnterpriseUserResult.
        :type: str
        """

        self._error = error

    @property
    def rows(self):
        """
        Gets the rows of this EnterpriseUserUpdateEnterpriseUserResult.
        The number of rows modified

        :return: The rows of this EnterpriseUserUpdateEnterpriseUserResult.
        :rtype: int
        """
        return self._rows

    @rows.setter
    def rows(self, rows):
        """
        Sets the rows of this EnterpriseUserUpdateEnterpriseUserResult.
        The number of rows modified

        :param rows: The rows of this EnterpriseUserUpdateEnterpriseUserResult.
        :type: int
        """

        self._rows = rows

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
        if not isinstance(other, EnterpriseUserUpdateEnterpriseUserResult):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
