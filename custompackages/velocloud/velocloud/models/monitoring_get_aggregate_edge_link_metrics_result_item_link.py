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


class MonitoringGetAggregateEdgeLinkMetricsResultItemLink(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, enterpriseName=None, enterpriseId=None, edgeName=None, edgeSerialNumber=None, edgeHASerialNumber=None, edgeState=None, edgeLastContact=None, edgeId=None, edgeSystemUpSince=None, edgeServiceUpSince=None, edgeModelNumber=None, isp=None, displayName=None, interface=None, linkId=None, linkState=None, linkLastActive=None, linkVpnState=None):
        """
        MonitoringGetAggregateEdgeLinkMetricsResultItemLink - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'enterpriseName': 'str',
            'enterpriseId': 'int',
            'edgeName': 'str',
            'edgeSerialNumber': 'str',
            'edgeHASerialNumber': 'str',
            'edgeState': 'str',
            'edgeLastContact': 'datetime',
            'edgeId': 'int',
            'edgeSystemUpSince': 'datetime',
            'edgeServiceUpSince': 'datetime',
            'edgeModelNumber': 'str',
            'isp': 'str',
            'displayName': 'str',
            'interface': 'str',
            'linkId': 'int',
            'linkState': 'str',
            'linkLastActive': 'datetime',
            'linkVpnState': 'str'
        }

        self.attribute_map = {
            'enterpriseName': 'enterpriseName',
            'enterpriseId': 'enterpriseId',
            'edgeName': 'edgeName',
            'edgeSerialNumber': 'edgeSerialNumber',
            'edgeHASerialNumber': 'edgeHASerialNumber',
            'edgeState': 'edgeState',
            'edgeLastContact': 'edgeLastContact',
            'edgeId': 'edgeId',
            'edgeSystemUpSince': 'edgeSystemUpSince',
            'edgeServiceUpSince': 'edgeServiceUpSince',
            'edgeModelNumber': 'edgeModelNumber',
            'isp': 'isp',
            'displayName': 'displayName',
            'interface': 'interface',
            'linkId': 'linkId',
            'linkState': 'linkState',
            'linkLastActive': 'linkLastActive',
            'linkVpnState': 'linkVpnState'
        }

        self._enterpriseName = enterpriseName
        self._enterpriseId = enterpriseId
        self._edgeName = edgeName
        self._edgeSerialNumber = edgeSerialNumber
        self._edgeHASerialNumber = edgeHASerialNumber
        self._edgeState = edgeState
        self._edgeLastContact = edgeLastContact
        self._edgeId = edgeId
        self._edgeSystemUpSince = edgeSystemUpSince
        self._edgeServiceUpSince = edgeServiceUpSince
        self._edgeModelNumber = edgeModelNumber
        self._isp = isp
        self._displayName = displayName
        self._interface = interface
        self._linkId = linkId
        self._linkState = linkState
        self._linkLastActive = linkLastActive
        self._linkVpnState = linkVpnState

    @property
    def enterpriseName(self):
        """
        Gets the enterpriseName of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The enterpriseName of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: str
        """
        return self._enterpriseName

    @enterpriseName.setter
    def enterpriseName(self, enterpriseName):
        """
        Sets the enterpriseName of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param enterpriseName: The enterpriseName of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: str
        """

        self._enterpriseName = enterpriseName

    @property
    def enterpriseId(self):
        """
        Gets the enterpriseId of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The enterpriseId of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: int
        """
        return self._enterpriseId

    @enterpriseId.setter
    def enterpriseId(self, enterpriseId):
        """
        Sets the enterpriseId of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param enterpriseId: The enterpriseId of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: int
        """

        self._enterpriseId = enterpriseId

    @property
    def edgeName(self):
        """
        Gets the edgeName of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The edgeName of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: str
        """
        return self._edgeName

    @edgeName.setter
    def edgeName(self, edgeName):
        """
        Sets the edgeName of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param edgeName: The edgeName of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: str
        """

        self._edgeName = edgeName

    @property
    def edgeSerialNumber(self):
        """
        Gets the edgeSerialNumber of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The edgeSerialNumber of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: str
        """
        return self._edgeSerialNumber

    @edgeSerialNumber.setter
    def edgeSerialNumber(self, edgeSerialNumber):
        """
        Sets the edgeSerialNumber of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param edgeSerialNumber: The edgeSerialNumber of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: str
        """

        self._edgeSerialNumber = edgeSerialNumber

    @property
    def edgeHASerialNumber(self):
        """
        Gets the edgeHASerialNumber of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The edgeHASerialNumber of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: str
        """
        return self._edgeHASerialNumber

    @edgeHASerialNumber.setter
    def edgeHASerialNumber(self, edgeHASerialNumber):
        """
        Sets the edgeHASerialNumber of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param edgeHASerialNumber: The edgeHASerialNumber of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: str
        """

        self._edgeHASerialNumber = edgeHASerialNumber

    @property
    def edgeState(self):
        """
        Gets the edgeState of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The edgeState of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: str
        """
        return self._edgeState

    @edgeState.setter
    def edgeState(self, edgeState):
        """
        Sets the edgeState of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param edgeState: The edgeState of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: str
        """

        self._edgeState = edgeState

    @property
    def edgeLastContact(self):
        """
        Gets the edgeLastContact of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The edgeLastContact of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: datetime
        """
        return self._edgeLastContact

    @edgeLastContact.setter
    def edgeLastContact(self, edgeLastContact):
        """
        Sets the edgeLastContact of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param edgeLastContact: The edgeLastContact of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: datetime
        """

        self._edgeLastContact = edgeLastContact

    @property
    def edgeId(self):
        """
        Gets the edgeId of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The edgeId of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: int
        """
        return self._edgeId

    @edgeId.setter
    def edgeId(self, edgeId):
        """
        Sets the edgeId of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param edgeId: The edgeId of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: int
        """

        self._edgeId = edgeId

    @property
    def edgeSystemUpSince(self):
        """
        Gets the edgeSystemUpSince of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The edgeSystemUpSince of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: datetime
        """
        return self._edgeSystemUpSince

    @edgeSystemUpSince.setter
    def edgeSystemUpSince(self, edgeSystemUpSince):
        """
        Sets the edgeSystemUpSince of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param edgeSystemUpSince: The edgeSystemUpSince of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: datetime
        """

        self._edgeSystemUpSince = edgeSystemUpSince

    @property
    def edgeServiceUpSince(self):
        """
        Gets the edgeServiceUpSince of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The edgeServiceUpSince of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: datetime
        """
        return self._edgeServiceUpSince

    @edgeServiceUpSince.setter
    def edgeServiceUpSince(self, edgeServiceUpSince):
        """
        Sets the edgeServiceUpSince of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param edgeServiceUpSince: The edgeServiceUpSince of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: datetime
        """

        self._edgeServiceUpSince = edgeServiceUpSince

    @property
    def edgeModelNumber(self):
        """
        Gets the edgeModelNumber of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The edgeModelNumber of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: str
        """
        return self._edgeModelNumber

    @edgeModelNumber.setter
    def edgeModelNumber(self, edgeModelNumber):
        """
        Sets the edgeModelNumber of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param edgeModelNumber: The edgeModelNumber of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: str
        """

        self._edgeModelNumber = edgeModelNumber

    @property
    def isp(self):
        """
        Gets the isp of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The isp of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: str
        """
        return self._isp

    @isp.setter
    def isp(self, isp):
        """
        Sets the isp of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param isp: The isp of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: str
        """

        self._isp = isp

    @property
    def displayName(self):
        """
        Gets the displayName of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The displayName of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: str
        """
        return self._displayName

    @displayName.setter
    def displayName(self, displayName):
        """
        Sets the displayName of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param displayName: The displayName of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: str
        """

        self._displayName = displayName

    @property
    def interface(self):
        """
        Gets the interface of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The interface of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: str
        """
        return self._interface

    @interface.setter
    def interface(self, interface):
        """
        Sets the interface of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param interface: The interface of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: str
        """

        self._interface = interface

    @property
    def linkId(self):
        """
        Gets the linkId of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The linkId of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: int
        """
        return self._linkId

    @linkId.setter
    def linkId(self, linkId):
        """
        Sets the linkId of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param linkId: The linkId of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: int
        """

        self._linkId = linkId

    @property
    def linkState(self):
        """
        Gets the linkState of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The linkState of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: str
        """
        return self._linkState

    @linkState.setter
    def linkState(self, linkState):
        """
        Sets the linkState of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param linkState: The linkState of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: str
        """

        self._linkState = linkState

    @property
    def linkLastActive(self):
        """
        Gets the linkLastActive of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The linkLastActive of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: datetime
        """
        return self._linkLastActive

    @linkLastActive.setter
    def linkLastActive(self, linkLastActive):
        """
        Sets the linkLastActive of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param linkLastActive: The linkLastActive of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: datetime
        """

        self._linkLastActive = linkLastActive

    @property
    def linkVpnState(self):
        """
        Gets the linkVpnState of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :return: The linkVpnState of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :rtype: str
        """
        return self._linkVpnState

    @linkVpnState.setter
    def linkVpnState(self, linkVpnState):
        """
        Sets the linkVpnState of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.

        :param linkVpnState: The linkVpnState of this MonitoringGetAggregateEdgeLinkMetricsResultItemLink.
        :type: str
        """

        self._linkVpnState = linkVpnState

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
        if not isinstance(other, MonitoringGetAggregateEdgeLinkMetricsResultItemLink):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
