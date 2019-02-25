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


class EnterpriseNetworkSpace(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, name=None, mode=None, cidrIp=None, cidrPrefix=None, maxVlans=None, vlans=None):
        """
        EnterpriseNetworkSpace - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'name': 'str',
            'mode': 'str',
            'cidrIp': 'str',
            'cidrPrefix': 'int',
            'maxVlans': 'int',
            'vlans': 'list[Vlan]'
        }

        self.attribute_map = {
            'name': 'name',
            'mode': 'mode',
            'cidrIp': 'cidrIp',
            'cidrPrefix': 'cidrPrefix',
            'maxVlans': 'maxVlans',
            'vlans': 'vlans'
        }

        self._name = name
        self._mode = mode
        self._cidrIp = cidrIp
        self._cidrPrefix = cidrPrefix
        self._maxVlans = maxVlans
        self._vlans = vlans

    @property
    def name(self):
        """
        Gets the name of this EnterpriseNetworkSpace.

        :return: The name of this EnterpriseNetworkSpace.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this EnterpriseNetworkSpace.

        :param name: The name of this EnterpriseNetworkSpace.
        :type: str
        """

        self._name = name

    @property
    def mode(self):
        """
        Gets the mode of this EnterpriseNetworkSpace.

        :return: The mode of this EnterpriseNetworkSpace.
        :rtype: str
        """
        return self._mode

    @mode.setter
    def mode(self, mode):
        """
        Sets the mode of this EnterpriseNetworkSpace.

        :param mode: The mode of this EnterpriseNetworkSpace.
        :type: str
        """

        self._mode = mode

    @property
    def cidrIp(self):
        """
        Gets the cidrIp of this EnterpriseNetworkSpace.

        :return: The cidrIp of this EnterpriseNetworkSpace.
        :rtype: str
        """
        return self._cidrIp

    @cidrIp.setter
    def cidrIp(self, cidrIp):
        """
        Sets the cidrIp of this EnterpriseNetworkSpace.

        :param cidrIp: The cidrIp of this EnterpriseNetworkSpace.
        :type: str
        """

        self._cidrIp = cidrIp

    @property
    def cidrPrefix(self):
        """
        Gets the cidrPrefix of this EnterpriseNetworkSpace.

        :return: The cidrPrefix of this EnterpriseNetworkSpace.
        :rtype: int
        """
        return self._cidrPrefix

    @cidrPrefix.setter
    def cidrPrefix(self, cidrPrefix):
        """
        Sets the cidrPrefix of this EnterpriseNetworkSpace.

        :param cidrPrefix: The cidrPrefix of this EnterpriseNetworkSpace.
        :type: int
        """

        self._cidrPrefix = cidrPrefix

    @property
    def maxVlans(self):
        """
        Gets the maxVlans of this EnterpriseNetworkSpace.

        :return: The maxVlans of this EnterpriseNetworkSpace.
        :rtype: int
        """
        return self._maxVlans

    @maxVlans.setter
    def maxVlans(self, maxVlans):
        """
        Sets the maxVlans of this EnterpriseNetworkSpace.

        :param maxVlans: The maxVlans of this EnterpriseNetworkSpace.
        :type: int
        """

        self._maxVlans = maxVlans

    @property
    def vlans(self):
        """
        Gets the vlans of this EnterpriseNetworkSpace.

        :return: The vlans of this EnterpriseNetworkSpace.
        :rtype: list[Vlan]
        """
        return self._vlans

    @vlans.setter
    def vlans(self, vlans):
        """
        Sets the vlans of this EnterpriseNetworkSpace.

        :param vlans: The vlans of this EnterpriseNetworkSpace.
        :type: list[Vlan]
        """

        self._vlans = vlans

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
        if not isinstance(other, EnterpriseNetworkSpace):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
