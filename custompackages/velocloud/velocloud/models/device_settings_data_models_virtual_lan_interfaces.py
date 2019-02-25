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


class DeviceSettingsDataModelsVirtualLanInterfaces(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, space=None, name=None, type=None, cwp=None, portMode=None, untaggedVlan=None, disabled=None, l2=None, vlanIds=None):
        """
        DeviceSettingsDataModelsVirtualLanInterfaces - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'space': 'str',
            'name': 'str',
            'type': 'str',
            'cwp': 'bool',
            'portMode': 'str',
            'untaggedVlan': 'str',
            'disabled': 'bool',
            'l2': 'EdgeDeviceSettingsDataL2',
            'vlanIds': 'list[int]'
        }

        self.attribute_map = {
            'space': 'space',
            'name': 'name',
            'type': 'type',
            'cwp': 'cwp',
            'portMode': 'portMode',
            'untaggedVlan': 'untaggedVlan',
            'disabled': 'disabled',
            'l2': 'l2',
            'vlanIds': 'vlanIds'
        }

        self._space = space
        self._name = name
        self._type = type
        self._cwp = cwp
        self._portMode = portMode
        self._untaggedVlan = untaggedVlan
        self._disabled = disabled
        self._l2 = l2
        self._vlanIds = vlanIds

    @property
    def space(self):
        """
        Gets the space of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :return: The space of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :rtype: str
        """
        return self._space

    @space.setter
    def space(self, space):
        """
        Sets the space of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :param space: The space of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :type: str
        """

        self._space = space

    @property
    def name(self):
        """
        Gets the name of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :return: The name of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :param name: The name of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :type: str
        """

        self._name = name

    @property
    def type(self):
        """
        Gets the type of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :return: The type of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        Sets the type of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :param type: The type of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :type: str
        """

        self._type = type

    @property
    def cwp(self):
        """
        Gets the cwp of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :return: The cwp of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :rtype: bool
        """
        return self._cwp

    @cwp.setter
    def cwp(self, cwp):
        """
        Sets the cwp of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :param cwp: The cwp of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :type: bool
        """

        self._cwp = cwp

    @property
    def portMode(self):
        """
        Gets the portMode of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :return: The portMode of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :rtype: str
        """
        return self._portMode

    @portMode.setter
    def portMode(self, portMode):
        """
        Sets the portMode of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :param portMode: The portMode of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :type: str
        """

        self._portMode = portMode

    @property
    def untaggedVlan(self):
        """
        Gets the untaggedVlan of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :return: The untaggedVlan of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :rtype: str
        """
        return self._untaggedVlan

    @untaggedVlan.setter
    def untaggedVlan(self, untaggedVlan):
        """
        Sets the untaggedVlan of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :param untaggedVlan: The untaggedVlan of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :type: str
        """

        self._untaggedVlan = untaggedVlan

    @property
    def disabled(self):
        """
        Gets the disabled of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :return: The disabled of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :rtype: bool
        """
        return self._disabled

    @disabled.setter
    def disabled(self, disabled):
        """
        Sets the disabled of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :param disabled: The disabled of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :type: bool
        """

        self._disabled = disabled

    @property
    def l2(self):
        """
        Gets the l2 of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :return: The l2 of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :rtype: EdgeDeviceSettingsDataL2
        """
        return self._l2

    @l2.setter
    def l2(self, l2):
        """
        Sets the l2 of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :param l2: The l2 of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :type: EdgeDeviceSettingsDataL2
        """

        self._l2 = l2

    @property
    def vlanIds(self):
        """
        Gets the vlanIds of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :return: The vlanIds of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :rtype: list[int]
        """
        return self._vlanIds

    @vlanIds.setter
    def vlanIds(self, vlanIds):
        """
        Sets the vlanIds of this DeviceSettingsDataModelsVirtualLanInterfaces.

        :param vlanIds: The vlanIds of this DeviceSettingsDataModelsVirtualLanInterfaces.
        :type: list[int]
        """

        self._vlanIds = vlanIds

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
        if not isinstance(other, DeviceSettingsDataModelsVirtualLanInterfaces):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
