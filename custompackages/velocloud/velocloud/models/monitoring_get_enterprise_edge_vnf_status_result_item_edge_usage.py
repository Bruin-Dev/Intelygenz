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


class MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, configurationId=None, edgeSpecificId=None, name=None, logicalId=None, profileId=None, vnfStatus=None):
        """
        MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'configurationId': 'int',
            'edgeSpecificId': 'int',
            'name': 'str',
            'logicalId': 'str',
            'profileId': 'int',
            'vnfStatus': 'MonitoringGetEnterpriseEdgeVnfStatusResultItemVnfStatus'
        }

        self.attribute_map = {
            'configurationId': 'configurationId',
            'edgeSpecificId': 'edgeSpecificId',
            'name': 'name',
            'logicalId': 'logicalId',
            'profileId': 'profileId',
            'vnfStatus': 'vnfStatus'
        }

        self._configurationId = configurationId
        self._edgeSpecificId = edgeSpecificId
        self._name = name
        self._logicalId = logicalId
        self._profileId = profileId
        self._vnfStatus = vnfStatus

    @property
    def configurationId(self):
        """
        Gets the configurationId of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.

        :return: The configurationId of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.
        :rtype: int
        """
        return self._configurationId

    @configurationId.setter
    def configurationId(self, configurationId):
        """
        Sets the configurationId of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.

        :param configurationId: The configurationId of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.
        :type: int
        """

        self._configurationId = configurationId

    @property
    def edgeSpecificId(self):
        """
        Gets the edgeSpecificId of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.

        :return: The edgeSpecificId of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.
        :rtype: int
        """
        return self._edgeSpecificId

    @edgeSpecificId.setter
    def edgeSpecificId(self, edgeSpecificId):
        """
        Sets the edgeSpecificId of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.

        :param edgeSpecificId: The edgeSpecificId of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.
        :type: int
        """

        self._edgeSpecificId = edgeSpecificId

    @property
    def name(self):
        """
        Gets the name of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.

        :return: The name of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.

        :param name: The name of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.
        :type: str
        """

        self._name = name

    @property
    def logicalId(self):
        """
        Gets the logicalId of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.

        :return: The logicalId of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.
        :rtype: str
        """
        return self._logicalId

    @logicalId.setter
    def logicalId(self, logicalId):
        """
        Sets the logicalId of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.

        :param logicalId: The logicalId of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.
        :type: str
        """

        self._logicalId = logicalId

    @property
    def profileId(self):
        """
        Gets the profileId of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.

        :return: The profileId of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.
        :rtype: int
        """
        return self._profileId

    @profileId.setter
    def profileId(self, profileId):
        """
        Sets the profileId of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.

        :param profileId: The profileId of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.
        :type: int
        """

        self._profileId = profileId

    @property
    def vnfStatus(self):
        """
        Gets the vnfStatus of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.

        :return: The vnfStatus of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.
        :rtype: MonitoringGetEnterpriseEdgeVnfStatusResultItemVnfStatus
        """
        return self._vnfStatus

    @vnfStatus.setter
    def vnfStatus(self, vnfStatus):
        """
        Sets the vnfStatus of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.

        :param vnfStatus: The vnfStatus of this MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage.
        :type: MonitoringGetEnterpriseEdgeVnfStatusResultItemVnfStatus
        """

        self._vnfStatus = vnfStatus

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
        if not isinstance(other, MonitoringGetEnterpriseEdgeVnfStatusResultItemEdgeUsage):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
