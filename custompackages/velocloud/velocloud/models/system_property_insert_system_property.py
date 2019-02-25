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


class SystemPropertyInsertSystemProperty(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, name=None, value=None, defaultValue=None, dataType=None, description=None, isPassword=None, isReadOnly=None):
        """
        SystemPropertyInsertSystemProperty - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'name': 'str',
            'value': 'str',
            'defaultValue': 'str',
            'dataType': 'str',
            'description': 'str',
            'isPassword': 'bool',
            'isReadOnly': 'bool'
        }

        self.attribute_map = {
            'name': 'name',
            'value': 'value',
            'defaultValue': 'defaultValue',
            'dataType': 'dataType',
            'description': 'description',
            'isPassword': 'isPassword',
            'isReadOnly': 'isReadOnly'
        }

        self._name = name
        self._value = value
        self._defaultValue = defaultValue
        self._dataType = dataType
        self._description = description
        self._isPassword = isPassword
        self._isReadOnly = isReadOnly

    @property
    def name(self):
        """
        Gets the name of this SystemPropertyInsertSystemProperty.

        :return: The name of this SystemPropertyInsertSystemProperty.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this SystemPropertyInsertSystemProperty.

        :param name: The name of this SystemPropertyInsertSystemProperty.
        :type: str
        """

        self._name = name

    @property
    def value(self):
        """
        Gets the value of this SystemPropertyInsertSystemProperty.

        :return: The value of this SystemPropertyInsertSystemProperty.
        :rtype: str
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Sets the value of this SystemPropertyInsertSystemProperty.

        :param value: The value of this SystemPropertyInsertSystemProperty.
        :type: str
        """

        self._value = value

    @property
    def defaultValue(self):
        """
        Gets the defaultValue of this SystemPropertyInsertSystemProperty.

        :return: The defaultValue of this SystemPropertyInsertSystemProperty.
        :rtype: str
        """
        return self._defaultValue

    @defaultValue.setter
    def defaultValue(self, defaultValue):
        """
        Sets the defaultValue of this SystemPropertyInsertSystemProperty.

        :param defaultValue: The defaultValue of this SystemPropertyInsertSystemProperty.
        :type: str
        """

        self._defaultValue = defaultValue

    @property
    def dataType(self):
        """
        Gets the dataType of this SystemPropertyInsertSystemProperty.

        :return: The dataType of this SystemPropertyInsertSystemProperty.
        :rtype: str
        """
        return self._dataType

    @dataType.setter
    def dataType(self, dataType):
        """
        Sets the dataType of this SystemPropertyInsertSystemProperty.

        :param dataType: The dataType of this SystemPropertyInsertSystemProperty.
        :type: str
        """

        self._dataType = dataType

    @property
    def description(self):
        """
        Gets the description of this SystemPropertyInsertSystemProperty.

        :return: The description of this SystemPropertyInsertSystemProperty.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this SystemPropertyInsertSystemProperty.

        :param description: The description of this SystemPropertyInsertSystemProperty.
        :type: str
        """

        self._description = description

    @property
    def isPassword(self):
        """
        Gets the isPassword of this SystemPropertyInsertSystemProperty.

        :return: The isPassword of this SystemPropertyInsertSystemProperty.
        :rtype: bool
        """
        return self._isPassword

    @isPassword.setter
    def isPassword(self, isPassword):
        """
        Sets the isPassword of this SystemPropertyInsertSystemProperty.

        :param isPassword: The isPassword of this SystemPropertyInsertSystemProperty.
        :type: bool
        """

        self._isPassword = isPassword

    @property
    def isReadOnly(self):
        """
        Gets the isReadOnly of this SystemPropertyInsertSystemProperty.

        :return: The isReadOnly of this SystemPropertyInsertSystemProperty.
        :rtype: bool
        """
        return self._isReadOnly

    @isReadOnly.setter
    def isReadOnly(self, isReadOnly):
        """
        Sets the isReadOnly of this SystemPropertyInsertSystemProperty.

        :param isReadOnly: The isReadOnly of this SystemPropertyInsertSystemProperty.
        :type: bool
        """

        self._isReadOnly = isReadOnly

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
        if not isinstance(other, SystemPropertyInsertSystemProperty):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
