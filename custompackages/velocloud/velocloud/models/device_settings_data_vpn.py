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


class DeviceSettingsDataVpn(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, enabled=None, edgeToDataCenter=None, ref=None, edgeToEdgeHub=None, edgeToEdge=None, edgeToEdgeDetail=None):
        """
        DeviceSettingsDataVpn - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'enabled': 'bool',
            'edgeToDataCenter': 'bool',
            'ref': 'str',
            'edgeToEdgeHub': 'DeviceSettingsDataVpnEdgeToEdgeHub',
            'edgeToEdge': 'bool',
            'edgeToEdgeDetail': 'DeviceSettingsDataVpnEdgeToEdgeDetail'
        }

        self.attribute_map = {
            'enabled': 'enabled',
            'edgeToDataCenter': 'edgeToDataCenter',
            'ref': 'ref',
            'edgeToEdgeHub': 'edgeToEdgeHub',
            'edgeToEdge': 'edgeToEdge',
            'edgeToEdgeDetail': 'edgeToEdgeDetail'
        }

        self._enabled = enabled
        self._edgeToDataCenter = edgeToDataCenter
        self._ref = ref
        self._edgeToEdgeHub = edgeToEdgeHub
        self._edgeToEdge = edgeToEdge
        self._edgeToEdgeDetail = edgeToEdgeDetail

    @property
    def enabled(self):
        """
        Gets the enabled of this DeviceSettingsDataVpn.

        :return: The enabled of this DeviceSettingsDataVpn.
        :rtype: bool
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        """
        Sets the enabled of this DeviceSettingsDataVpn.

        :param enabled: The enabled of this DeviceSettingsDataVpn.
        :type: bool
        """

        self._enabled = enabled

    @property
    def edgeToDataCenter(self):
        """
        Gets the edgeToDataCenter of this DeviceSettingsDataVpn.

        :return: The edgeToDataCenter of this DeviceSettingsDataVpn.
        :rtype: bool
        """
        return self._edgeToDataCenter

    @edgeToDataCenter.setter
    def edgeToDataCenter(self, edgeToDataCenter):
        """
        Sets the edgeToDataCenter of this DeviceSettingsDataVpn.

        :param edgeToDataCenter: The edgeToDataCenter of this DeviceSettingsDataVpn.
        :type: bool
        """

        self._edgeToDataCenter = edgeToDataCenter

    @property
    def ref(self):
        """
        Gets the ref of this DeviceSettingsDataVpn.

        :return: The ref of this DeviceSettingsDataVpn.
        :rtype: str
        """
        return self._ref

    @ref.setter
    def ref(self, ref):
        """
        Sets the ref of this DeviceSettingsDataVpn.

        :param ref: The ref of this DeviceSettingsDataVpn.
        :type: str
        """

        self._ref = ref

    @property
    def edgeToEdgeHub(self):
        """
        Gets the edgeToEdgeHub of this DeviceSettingsDataVpn.

        :return: The edgeToEdgeHub of this DeviceSettingsDataVpn.
        :rtype: DeviceSettingsDataVpnEdgeToEdgeHub
        """
        return self._edgeToEdgeHub

    @edgeToEdgeHub.setter
    def edgeToEdgeHub(self, edgeToEdgeHub):
        """
        Sets the edgeToEdgeHub of this DeviceSettingsDataVpn.

        :param edgeToEdgeHub: The edgeToEdgeHub of this DeviceSettingsDataVpn.
        :type: DeviceSettingsDataVpnEdgeToEdgeHub
        """

        self._edgeToEdgeHub = edgeToEdgeHub

    @property
    def edgeToEdge(self):
        """
        Gets the edgeToEdge of this DeviceSettingsDataVpn.

        :return: The edgeToEdge of this DeviceSettingsDataVpn.
        :rtype: bool
        """
        return self._edgeToEdge

    @edgeToEdge.setter
    def edgeToEdge(self, edgeToEdge):
        """
        Sets the edgeToEdge of this DeviceSettingsDataVpn.

        :param edgeToEdge: The edgeToEdge of this DeviceSettingsDataVpn.
        :type: bool
        """

        self._edgeToEdge = edgeToEdge

    @property
    def edgeToEdgeDetail(self):
        """
        Gets the edgeToEdgeDetail of this DeviceSettingsDataVpn.

        :return: The edgeToEdgeDetail of this DeviceSettingsDataVpn.
        :rtype: DeviceSettingsDataVpnEdgeToEdgeDetail
        """
        return self._edgeToEdgeDetail

    @edgeToEdgeDetail.setter
    def edgeToEdgeDetail(self, edgeToEdgeDetail):
        """
        Sets the edgeToEdgeDetail of this DeviceSettingsDataVpn.

        :param edgeToEdgeDetail: The edgeToEdgeDetail of this DeviceSettingsDataVpn.
        :type: DeviceSettingsDataVpnEdgeToEdgeDetail
        """

        self._edgeToEdgeDetail = edgeToEdgeDetail

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
        if not isinstance(other, DeviceSettingsDataVpn):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
