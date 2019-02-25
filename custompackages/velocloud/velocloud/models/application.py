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


class Application(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, _class=None, description=None, displayName=None, id=None, knownIpPortMapping=None, protocolPortMapping=None):
        """
        Application - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            '_class': 'int',
            'description': 'str',
            'displayName': 'str',
            'id': 'int',
            'knownIpPortMapping': 'IpPortMapping',
            'protocolPortMapping': 'ProtocolPortMapping'
        }

        self.attribute_map = {
            '_class': 'class',
            'description': 'description',
            'displayName': 'displayName',
            'id': 'id',
            'knownIpPortMapping': 'knownIpPortMapping',
            'protocolPortMapping': 'protocolPortMapping'
        }

        self.__class = _class
        self._description = description
        self._displayName = displayName
        self._id = id
        self._knownIpPortMapping = knownIpPortMapping
        self._protocolPortMapping = protocolPortMapping

    @property
    def _class(self):
        """
        Gets the _class of this Application.

        :return: The _class of this Application.
        :rtype: int
        """
        return self.__class

    @_class.setter
    def _class(self, _class):
        """
        Sets the _class of this Application.

        :param _class: The _class of this Application.
        :type: int
        """

        self.__class = _class

    @property
    def description(self):
        """
        Gets the description of this Application.

        :return: The description of this Application.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this Application.

        :param description: The description of this Application.
        :type: str
        """

        self._description = description

    @property
    def displayName(self):
        """
        Gets the displayName of this Application.

        :return: The displayName of this Application.
        :rtype: str
        """
        return self._displayName

    @displayName.setter
    def displayName(self, displayName):
        """
        Sets the displayName of this Application.

        :param displayName: The displayName of this Application.
        :type: str
        """

        self._displayName = displayName

    @property
    def id(self):
        """
        Gets the id of this Application.

        :return: The id of this Application.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this Application.

        :param id: The id of this Application.
        :type: int
        """

        self._id = id

    @property
    def knownIpPortMapping(self):
        """
        Gets the knownIpPortMapping of this Application.

        :return: The knownIpPortMapping of this Application.
        :rtype: IpPortMapping
        """
        return self._knownIpPortMapping

    @knownIpPortMapping.setter
    def knownIpPortMapping(self, knownIpPortMapping):
        """
        Sets the knownIpPortMapping of this Application.

        :param knownIpPortMapping: The knownIpPortMapping of this Application.
        :type: IpPortMapping
        """

        self._knownIpPortMapping = knownIpPortMapping

    @property
    def protocolPortMapping(self):
        """
        Gets the protocolPortMapping of this Application.

        :return: The protocolPortMapping of this Application.
        :rtype: ProtocolPortMapping
        """
        return self._protocolPortMapping

    @protocolPortMapping.setter
    def protocolPortMapping(self, protocolPortMapping):
        """
        Sets the protocolPortMapping of this Application.

        :param protocolPortMapping: The protocolPortMapping of this Application.
        :type: ProtocolPortMapping
        """

        self._protocolPortMapping = protocolPortMapping

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
        if not isinstance(other, Application):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
