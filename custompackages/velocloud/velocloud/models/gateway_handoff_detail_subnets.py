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


class GatewayHandoffDetailSubnets(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, name=None, routeCost=None, cidrIp=None, cidrPrefix=None, encrypt=None, handOffType=None):
        """
        GatewayHandoffDetailSubnets - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'name': 'str',
            'routeCost': 'int',
            'cidrIp': 'str',
            'cidrPrefix': 'int',
            'encrypt': 'bool',
            'handOffType': 'str'
        }

        self.attribute_map = {
            'name': 'name',
            'routeCost': 'routeCost',
            'cidrIp': 'cidrIp',
            'cidrPrefix': 'cidrPrefix',
            'encrypt': 'encrypt',
            'handOffType': 'handOffType'
        }

        self._name = name
        self._routeCost = routeCost
        self._cidrIp = cidrIp
        self._cidrPrefix = cidrPrefix
        self._encrypt = encrypt
        self._handOffType = handOffType

    @property
    def name(self):
        """
        Gets the name of this GatewayHandoffDetailSubnets.

        :return: The name of this GatewayHandoffDetailSubnets.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this GatewayHandoffDetailSubnets.

        :param name: The name of this GatewayHandoffDetailSubnets.
        :type: str
        """

        self._name = name

    @property
    def routeCost(self):
        """
        Gets the routeCost of this GatewayHandoffDetailSubnets.

        :return: The routeCost of this GatewayHandoffDetailSubnets.
        :rtype: int
        """
        return self._routeCost

    @routeCost.setter
    def routeCost(self, routeCost):
        """
        Sets the routeCost of this GatewayHandoffDetailSubnets.

        :param routeCost: The routeCost of this GatewayHandoffDetailSubnets.
        :type: int
        """

        self._routeCost = routeCost

    @property
    def cidrIp(self):
        """
        Gets the cidrIp of this GatewayHandoffDetailSubnets.

        :return: The cidrIp of this GatewayHandoffDetailSubnets.
        :rtype: str
        """
        return self._cidrIp

    @cidrIp.setter
    def cidrIp(self, cidrIp):
        """
        Sets the cidrIp of this GatewayHandoffDetailSubnets.

        :param cidrIp: The cidrIp of this GatewayHandoffDetailSubnets.
        :type: str
        """

        self._cidrIp = cidrIp

    @property
    def cidrPrefix(self):
        """
        Gets the cidrPrefix of this GatewayHandoffDetailSubnets.

        :return: The cidrPrefix of this GatewayHandoffDetailSubnets.
        :rtype: int
        """
        return self._cidrPrefix

    @cidrPrefix.setter
    def cidrPrefix(self, cidrPrefix):
        """
        Sets the cidrPrefix of this GatewayHandoffDetailSubnets.

        :param cidrPrefix: The cidrPrefix of this GatewayHandoffDetailSubnets.
        :type: int
        """

        self._cidrPrefix = cidrPrefix

    @property
    def encrypt(self):
        """
        Gets the encrypt of this GatewayHandoffDetailSubnets.

        :return: The encrypt of this GatewayHandoffDetailSubnets.
        :rtype: bool
        """
        return self._encrypt

    @encrypt.setter
    def encrypt(self, encrypt):
        """
        Sets the encrypt of this GatewayHandoffDetailSubnets.

        :param encrypt: The encrypt of this GatewayHandoffDetailSubnets.
        :type: bool
        """

        self._encrypt = encrypt

    @property
    def handOffType(self):
        """
        Gets the handOffType of this GatewayHandoffDetailSubnets.

        :return: The handOffType of this GatewayHandoffDetailSubnets.
        :rtype: str
        """
        return self._handOffType

    @handOffType.setter
    def handOffType(self, handOffType):
        """
        Sets the handOffType of this GatewayHandoffDetailSubnets.

        :param handOffType: The handOffType of this GatewayHandoffDetailSubnets.
        :type: str
        """

        self._handOffType = handOffType

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
        if not isinstance(other, GatewayHandoffDetailSubnets):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
