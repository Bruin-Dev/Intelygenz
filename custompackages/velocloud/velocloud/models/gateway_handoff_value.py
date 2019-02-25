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


class GatewayHandoffValue(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, bgpPrioritySetup=None, type=None, override=False, cTag=None, sTag=None, localAddress=None, staticRoutes=None, bgp=None, bgpInboundMap=None, bgpOutboundMap=None, overrides=None):
        """
        GatewayHandoffValue - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'bgpPrioritySetup': 'GatewayHandoffValueBgpPrioritySetup',
            'type': 'str',
            'override': 'bool',
            'cTag': 'int',
            'sTag': 'int',
            'localAddress': 'GatewayHandoffValueLocalAddress',
            'staticRoutes': 'GatewayHandoffValueStaticRoutes',
            'bgp': 'GatewayHandoffValueBgp',
            'bgpInboundMap': 'GatewayHandoffBgpRulesMap',
            'bgpOutboundMap': 'GatewayHandoffBgpRulesMap',
            'overrides': 'GatewayHandoffValueOverrides'
        }

        self.attribute_map = {
            'bgpPrioritySetup': 'bgpPrioritySetup',
            'type': 'type',
            'override': 'override',
            'cTag': 'cTag',
            'sTag': 'sTag',
            'localAddress': 'localAddress',
            'staticRoutes': 'staticRoutes',
            'bgp': 'bgp',
            'bgpInboundMap': 'bgpInboundMap',
            'bgpOutboundMap': 'bgpOutboundMap',
            'overrides': 'overrides'
        }

        self._bgpPrioritySetup = bgpPrioritySetup
        self._type = type
        self._override = override
        self._cTag = cTag
        self._sTag = sTag
        self._localAddress = localAddress
        self._staticRoutes = staticRoutes
        self._bgp = bgp
        self._bgpInboundMap = bgpInboundMap
        self._bgpOutboundMap = bgpOutboundMap
        self._overrides = overrides

    @property
    def bgpPrioritySetup(self):
        """
        Gets the bgpPrioritySetup of this GatewayHandoffValue.

        :return: The bgpPrioritySetup of this GatewayHandoffValue.
        :rtype: GatewayHandoffValueBgpPrioritySetup
        """
        return self._bgpPrioritySetup

    @bgpPrioritySetup.setter
    def bgpPrioritySetup(self, bgpPrioritySetup):
        """
        Sets the bgpPrioritySetup of this GatewayHandoffValue.

        :param bgpPrioritySetup: The bgpPrioritySetup of this GatewayHandoffValue.
        :type: GatewayHandoffValueBgpPrioritySetup
        """

        self._bgpPrioritySetup = bgpPrioritySetup

    @property
    def type(self):
        """
        Gets the type of this GatewayHandoffValue.

        :return: The type of this GatewayHandoffValue.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        Sets the type of this GatewayHandoffValue.

        :param type: The type of this GatewayHandoffValue.
        :type: str
        """

        self._type = type

    @property
    def override(self):
        """
        Gets the override of this GatewayHandoffValue.

        :return: The override of this GatewayHandoffValue.
        :rtype: bool
        """
        return self._override

    @override.setter
    def override(self, override):
        """
        Sets the override of this GatewayHandoffValue.

        :param override: The override of this GatewayHandoffValue.
        :type: bool
        """

        self._override = override

    @property
    def cTag(self):
        """
        Gets the cTag of this GatewayHandoffValue.

        :return: The cTag of this GatewayHandoffValue.
        :rtype: int
        """
        return self._cTag

    @cTag.setter
    def cTag(self, cTag):
        """
        Sets the cTag of this GatewayHandoffValue.

        :param cTag: The cTag of this GatewayHandoffValue.
        :type: int
        """

        self._cTag = cTag

    @property
    def sTag(self):
        """
        Gets the sTag of this GatewayHandoffValue.

        :return: The sTag of this GatewayHandoffValue.
        :rtype: int
        """
        return self._sTag

    @sTag.setter
    def sTag(self, sTag):
        """
        Sets the sTag of this GatewayHandoffValue.

        :param sTag: The sTag of this GatewayHandoffValue.
        :type: int
        """

        self._sTag = sTag

    @property
    def localAddress(self):
        """
        Gets the localAddress of this GatewayHandoffValue.

        :return: The localAddress of this GatewayHandoffValue.
        :rtype: GatewayHandoffValueLocalAddress
        """
        return self._localAddress

    @localAddress.setter
    def localAddress(self, localAddress):
        """
        Sets the localAddress of this GatewayHandoffValue.

        :param localAddress: The localAddress of this GatewayHandoffValue.
        :type: GatewayHandoffValueLocalAddress
        """

        self._localAddress = localAddress

    @property
    def staticRoutes(self):
        """
        Gets the staticRoutes of this GatewayHandoffValue.

        :return: The staticRoutes of this GatewayHandoffValue.
        :rtype: GatewayHandoffValueStaticRoutes
        """
        return self._staticRoutes

    @staticRoutes.setter
    def staticRoutes(self, staticRoutes):
        """
        Sets the staticRoutes of this GatewayHandoffValue.

        :param staticRoutes: The staticRoutes of this GatewayHandoffValue.
        :type: GatewayHandoffValueStaticRoutes
        """

        self._staticRoutes = staticRoutes

    @property
    def bgp(self):
        """
        Gets the bgp of this GatewayHandoffValue.

        :return: The bgp of this GatewayHandoffValue.
        :rtype: GatewayHandoffValueBgp
        """
        return self._bgp

    @bgp.setter
    def bgp(self, bgp):
        """
        Sets the bgp of this GatewayHandoffValue.

        :param bgp: The bgp of this GatewayHandoffValue.
        :type: GatewayHandoffValueBgp
        """

        self._bgp = bgp

    @property
    def bgpInboundMap(self):
        """
        Gets the bgpInboundMap of this GatewayHandoffValue.

        :return: The bgpInboundMap of this GatewayHandoffValue.
        :rtype: GatewayHandoffBgpRulesMap
        """
        return self._bgpInboundMap

    @bgpInboundMap.setter
    def bgpInboundMap(self, bgpInboundMap):
        """
        Sets the bgpInboundMap of this GatewayHandoffValue.

        :param bgpInboundMap: The bgpInboundMap of this GatewayHandoffValue.
        :type: GatewayHandoffBgpRulesMap
        """

        self._bgpInboundMap = bgpInboundMap

    @property
    def bgpOutboundMap(self):
        """
        Gets the bgpOutboundMap of this GatewayHandoffValue.

        :return: The bgpOutboundMap of this GatewayHandoffValue.
        :rtype: GatewayHandoffBgpRulesMap
        """
        return self._bgpOutboundMap

    @bgpOutboundMap.setter
    def bgpOutboundMap(self, bgpOutboundMap):
        """
        Sets the bgpOutboundMap of this GatewayHandoffValue.

        :param bgpOutboundMap: The bgpOutboundMap of this GatewayHandoffValue.
        :type: GatewayHandoffBgpRulesMap
        """

        self._bgpOutboundMap = bgpOutboundMap

    @property
    def overrides(self):
        """
        Gets the overrides of this GatewayHandoffValue.

        :return: The overrides of this GatewayHandoffValue.
        :rtype: GatewayHandoffValueOverrides
        """
        return self._overrides

    @overrides.setter
    def overrides(self, overrides):
        """
        Sets the overrides of this GatewayHandoffValue.

        :param overrides: The overrides of this GatewayHandoffValue.
        :type: GatewayHandoffValueOverrides
        """

        self._overrides = overrides

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
        if not isinstance(other, GatewayHandoffValue):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
