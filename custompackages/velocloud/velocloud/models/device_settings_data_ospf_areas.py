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


class DeviceSettingsDataOspfAreas(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, id=None, name=None, type=None):
        """
        DeviceSettingsDataOspfAreas - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'int',
            'name': 'str',
            'type': 'str'
        }

        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'type': 'type'
        }

        self._id = id
        self._name = name
        self._type = type

    @property
    def id(self):
        """
        Gets the id of this DeviceSettingsDataOspfAreas.

        :return: The id of this DeviceSettingsDataOspfAreas.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this DeviceSettingsDataOspfAreas.

        :param id: The id of this DeviceSettingsDataOspfAreas.
        :type: int
        """

        self._id = id

    @property
    def name(self):
        """
        Gets the name of this DeviceSettingsDataOspfAreas.

        :return: The name of this DeviceSettingsDataOspfAreas.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this DeviceSettingsDataOspfAreas.

        :param name: The name of this DeviceSettingsDataOspfAreas.
        :type: str
        """

        self._name = name

    @property
    def type(self):
        """
        Gets the type of this DeviceSettingsDataOspfAreas.

        :return: The type of this DeviceSettingsDataOspfAreas.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        Sets the type of this DeviceSettingsDataOspfAreas.

        :param type: The type of this DeviceSettingsDataOspfAreas.
        :type: str
        """

        self._type = type

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
        if not isinstance(other, DeviceSettingsDataOspfAreas):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
