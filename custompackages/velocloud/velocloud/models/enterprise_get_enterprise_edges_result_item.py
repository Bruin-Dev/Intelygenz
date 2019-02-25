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


class EnterpriseGetEnterpriseEdgesResultItem(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, activationKey=None, activationKeyExpires=None, activationState=None, activationTime=None, alertsEnabled=None, buildNumber=None, created=None, description=None, deviceFamily=None, deviceId=None, dnsName=None, edgeHardwareId=None, edgeState=None, edgeStateTime=None, endpointPkiMode=None, enterpriseId=None, haLastContact=None, haPreviousState=None, haSerialNumber=None, haState=None, id=None, isLive=None, lastContact=None, logicalId=None, modelNumber=None, modified=None, name=None, operatorAlertsEnabled=None, selfMacAddress=None, serialNumber=None, serviceState=None, serviceUpSince=None, siteId=None, softwareUpdated=None, softwareVersion=None, systemUpSince=None, configuration=None, links=None, recentLinks=None, site=None):
        """
        EnterpriseGetEnterpriseEdgesResultItem - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'activationKey': 'str',
            'activationKeyExpires': 'str',
            'activationState': 'str',
            'activationTime': 'str',
            'alertsEnabled': 'int',
            'buildNumber': 'str',
            'created': 'str',
            'description': 'str',
            'deviceFamily': 'str',
            'deviceId': 'str',
            'dnsName': 'str',
            'edgeHardwareId': 'str',
            'edgeState': 'str',
            'edgeStateTime': 'str',
            'endpointPkiMode': 'str',
            'enterpriseId': 'int',
            'haLastContact': 'str',
            'haPreviousState': 'str',
            'haSerialNumber': 'str',
            'haState': 'str',
            'id': 'int',
            'isLive': 'int',
            'lastContact': 'str',
            'logicalId': 'str',
            'modelNumber': 'str',
            'modified': 'str',
            'name': 'str',
            'operatorAlertsEnabled': 'int',
            'selfMacAddress': 'str',
            'serialNumber': 'str',
            'serviceState': 'str',
            'serviceUpSince': 'str',
            'siteId': 'int',
            'softwareUpdated': 'str',
            'softwareVersion': 'str',
            'systemUpSince': 'str',
            'configuration': 'ModelConfiguration',
            'links': 'list[Link]',
            'recentLinks': 'list[Link]',
            'site': 'Site'
        }

        self.attribute_map = {
            'activationKey': 'activationKey',
            'activationKeyExpires': 'activationKeyExpires',
            'activationState': 'activationState',
            'activationTime': 'activationTime',
            'alertsEnabled': 'alertsEnabled',
            'buildNumber': 'buildNumber',
            'created': 'created',
            'description': 'description',
            'deviceFamily': 'deviceFamily',
            'deviceId': 'deviceId',
            'dnsName': 'dnsName',
            'edgeHardwareId': 'edgeHardwareId',
            'edgeState': 'edgeState',
            'edgeStateTime': 'edgeStateTime',
            'endpointPkiMode': 'endpointPkiMode',
            'enterpriseId': 'enterpriseId',
            'haLastContact': 'haLastContact',
            'haPreviousState': 'haPreviousState',
            'haSerialNumber': 'haSerialNumber',
            'haState': 'haState',
            'id': 'id',
            'isLive': 'isLive',
            'lastContact': 'lastContact',
            'logicalId': 'logicalId',
            'modelNumber': 'modelNumber',
            'modified': 'modified',
            'name': 'name',
            'operatorAlertsEnabled': 'operatorAlertsEnabled',
            'selfMacAddress': 'selfMacAddress',
            'serialNumber': 'serialNumber',
            'serviceState': 'serviceState',
            'serviceUpSince': 'serviceUpSince',
            'siteId': 'siteId',
            'softwareUpdated': 'softwareUpdated',
            'softwareVersion': 'softwareVersion',
            'systemUpSince': 'systemUpSince',
            'configuration': 'configuration',
            'links': 'links',
            'recentLinks': 'recentLinks',
            'site': 'site'
        }

        self._activationKey = activationKey
        self._activationKeyExpires = activationKeyExpires
        self._activationState = activationState
        self._activationTime = activationTime
        self._alertsEnabled = alertsEnabled
        self._buildNumber = buildNumber
        self._created = created
        self._description = description
        self._deviceFamily = deviceFamily
        self._deviceId = deviceId
        self._dnsName = dnsName
        self._edgeHardwareId = edgeHardwareId
        self._edgeState = edgeState
        self._edgeStateTime = edgeStateTime
        self._endpointPkiMode = endpointPkiMode
        self._enterpriseId = enterpriseId
        self._haLastContact = haLastContact
        self._haPreviousState = haPreviousState
        self._haSerialNumber = haSerialNumber
        self._haState = haState
        self._id = id
        self._isLive = isLive
        self._lastContact = lastContact
        self._logicalId = logicalId
        self._modelNumber = modelNumber
        self._modified = modified
        self._name = name
        self._operatorAlertsEnabled = operatorAlertsEnabled
        self._selfMacAddress = selfMacAddress
        self._serialNumber = serialNumber
        self._serviceState = serviceState
        self._serviceUpSince = serviceUpSince
        self._siteId = siteId
        self._softwareUpdated = softwareUpdated
        self._softwareVersion = softwareVersion
        self._systemUpSince = systemUpSince
        self._configuration = configuration
        self._links = links
        self._recentLinks = recentLinks
        self._site = site

    @property
    def activationKey(self):
        """
        Gets the activationKey of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The activationKey of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._activationKey

    @activationKey.setter
    def activationKey(self, activationKey):
        """
        Sets the activationKey of this EnterpriseGetEnterpriseEdgesResultItem.

        :param activationKey: The activationKey of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._activationKey = activationKey

    @property
    def activationKeyExpires(self):
        """
        Gets the activationKeyExpires of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The activationKeyExpires of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._activationKeyExpires

    @activationKeyExpires.setter
    def activationKeyExpires(self, activationKeyExpires):
        """
        Sets the activationKeyExpires of this EnterpriseGetEnterpriseEdgesResultItem.

        :param activationKeyExpires: The activationKeyExpires of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._activationKeyExpires = activationKeyExpires

    @property
    def activationState(self):
        """
        Gets the activationState of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The activationState of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._activationState

    @activationState.setter
    def activationState(self, activationState):
        """
        Sets the activationState of this EnterpriseGetEnterpriseEdgesResultItem.

        :param activationState: The activationState of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._activationState = activationState

    @property
    def activationTime(self):
        """
        Gets the activationTime of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The activationTime of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._activationTime

    @activationTime.setter
    def activationTime(self, activationTime):
        """
        Sets the activationTime of this EnterpriseGetEnterpriseEdgesResultItem.

        :param activationTime: The activationTime of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._activationTime = activationTime

    @property
    def alertsEnabled(self):
        """
        Gets the alertsEnabled of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The alertsEnabled of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: int
        """
        return self._alertsEnabled

    @alertsEnabled.setter
    def alertsEnabled(self, alertsEnabled):
        """
        Sets the alertsEnabled of this EnterpriseGetEnterpriseEdgesResultItem.

        :param alertsEnabled: The alertsEnabled of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: int
        """

        self._alertsEnabled = alertsEnabled

    @property
    def buildNumber(self):
        """
        Gets the buildNumber of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The buildNumber of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._buildNumber

    @buildNumber.setter
    def buildNumber(self, buildNumber):
        """
        Sets the buildNumber of this EnterpriseGetEnterpriseEdgesResultItem.

        :param buildNumber: The buildNumber of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._buildNumber = buildNumber

    @property
    def created(self):
        """
        Gets the created of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The created of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._created

    @created.setter
    def created(self, created):
        """
        Sets the created of this EnterpriseGetEnterpriseEdgesResultItem.

        :param created: The created of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._created = created

    @property
    def description(self):
        """
        Gets the description of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The description of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this EnterpriseGetEnterpriseEdgesResultItem.

        :param description: The description of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._description = description

    @property
    def deviceFamily(self):
        """
        Gets the deviceFamily of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The deviceFamily of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._deviceFamily

    @deviceFamily.setter
    def deviceFamily(self, deviceFamily):
        """
        Sets the deviceFamily of this EnterpriseGetEnterpriseEdgesResultItem.

        :param deviceFamily: The deviceFamily of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._deviceFamily = deviceFamily

    @property
    def deviceId(self):
        """
        Gets the deviceId of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The deviceId of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._deviceId

    @deviceId.setter
    def deviceId(self, deviceId):
        """
        Sets the deviceId of this EnterpriseGetEnterpriseEdgesResultItem.

        :param deviceId: The deviceId of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._deviceId = deviceId

    @property
    def dnsName(self):
        """
        Gets the dnsName of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The dnsName of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._dnsName

    @dnsName.setter
    def dnsName(self, dnsName):
        """
        Sets the dnsName of this EnterpriseGetEnterpriseEdgesResultItem.

        :param dnsName: The dnsName of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._dnsName = dnsName

    @property
    def edgeHardwareId(self):
        """
        Gets the edgeHardwareId of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The edgeHardwareId of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._edgeHardwareId

    @edgeHardwareId.setter
    def edgeHardwareId(self, edgeHardwareId):
        """
        Sets the edgeHardwareId of this EnterpriseGetEnterpriseEdgesResultItem.

        :param edgeHardwareId: The edgeHardwareId of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._edgeHardwareId = edgeHardwareId

    @property
    def edgeState(self):
        """
        Gets the edgeState of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The edgeState of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._edgeState

    @edgeState.setter
    def edgeState(self, edgeState):
        """
        Sets the edgeState of this EnterpriseGetEnterpriseEdgesResultItem.

        :param edgeState: The edgeState of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._edgeState = edgeState

    @property
    def edgeStateTime(self):
        """
        Gets the edgeStateTime of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The edgeStateTime of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._edgeStateTime

    @edgeStateTime.setter
    def edgeStateTime(self, edgeStateTime):
        """
        Sets the edgeStateTime of this EnterpriseGetEnterpriseEdgesResultItem.

        :param edgeStateTime: The edgeStateTime of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._edgeStateTime = edgeStateTime

    @property
    def endpointPkiMode(self):
        """
        Gets the endpointPkiMode of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The endpointPkiMode of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._endpointPkiMode

    @endpointPkiMode.setter
    def endpointPkiMode(self, endpointPkiMode):
        """
        Sets the endpointPkiMode of this EnterpriseGetEnterpriseEdgesResultItem.

        :param endpointPkiMode: The endpointPkiMode of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._endpointPkiMode = endpointPkiMode

    @property
    def enterpriseId(self):
        """
        Gets the enterpriseId of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The enterpriseId of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: int
        """
        return self._enterpriseId

    @enterpriseId.setter
    def enterpriseId(self, enterpriseId):
        """
        Sets the enterpriseId of this EnterpriseGetEnterpriseEdgesResultItem.

        :param enterpriseId: The enterpriseId of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: int
        """

        self._enterpriseId = enterpriseId

    @property
    def haLastContact(self):
        """
        Gets the haLastContact of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The haLastContact of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._haLastContact

    @haLastContact.setter
    def haLastContact(self, haLastContact):
        """
        Sets the haLastContact of this EnterpriseGetEnterpriseEdgesResultItem.

        :param haLastContact: The haLastContact of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._haLastContact = haLastContact

    @property
    def haPreviousState(self):
        """
        Gets the haPreviousState of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The haPreviousState of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._haPreviousState

    @haPreviousState.setter
    def haPreviousState(self, haPreviousState):
        """
        Sets the haPreviousState of this EnterpriseGetEnterpriseEdgesResultItem.

        :param haPreviousState: The haPreviousState of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._haPreviousState = haPreviousState

    @property
    def haSerialNumber(self):
        """
        Gets the haSerialNumber of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The haSerialNumber of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._haSerialNumber

    @haSerialNumber.setter
    def haSerialNumber(self, haSerialNumber):
        """
        Sets the haSerialNumber of this EnterpriseGetEnterpriseEdgesResultItem.

        :param haSerialNumber: The haSerialNumber of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._haSerialNumber = haSerialNumber

    @property
    def haState(self):
        """
        Gets the haState of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The haState of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._haState

    @haState.setter
    def haState(self, haState):
        """
        Sets the haState of this EnterpriseGetEnterpriseEdgesResultItem.

        :param haState: The haState of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._haState = haState

    @property
    def id(self):
        """
        Gets the id of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The id of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this EnterpriseGetEnterpriseEdgesResultItem.

        :param id: The id of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: int
        """

        self._id = id

    @property
    def isLive(self):
        """
        Gets the isLive of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The isLive of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: int
        """
        return self._isLive

    @isLive.setter
    def isLive(self, isLive):
        """
        Sets the isLive of this EnterpriseGetEnterpriseEdgesResultItem.

        :param isLive: The isLive of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: int
        """

        self._isLive = isLive

    @property
    def lastContact(self):
        """
        Gets the lastContact of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The lastContact of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._lastContact

    @lastContact.setter
    def lastContact(self, lastContact):
        """
        Sets the lastContact of this EnterpriseGetEnterpriseEdgesResultItem.

        :param lastContact: The lastContact of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._lastContact = lastContact

    @property
    def logicalId(self):
        """
        Gets the logicalId of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The logicalId of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._logicalId

    @logicalId.setter
    def logicalId(self, logicalId):
        """
        Sets the logicalId of this EnterpriseGetEnterpriseEdgesResultItem.

        :param logicalId: The logicalId of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._logicalId = logicalId

    @property
    def modelNumber(self):
        """
        Gets the modelNumber of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The modelNumber of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._modelNumber

    @modelNumber.setter
    def modelNumber(self, modelNumber):
        """
        Sets the modelNumber of this EnterpriseGetEnterpriseEdgesResultItem.

        :param modelNumber: The modelNumber of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._modelNumber = modelNumber

    @property
    def modified(self):
        """
        Gets the modified of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The modified of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._modified

    @modified.setter
    def modified(self, modified):
        """
        Sets the modified of this EnterpriseGetEnterpriseEdgesResultItem.

        :param modified: The modified of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._modified = modified

    @property
    def name(self):
        """
        Gets the name of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The name of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this EnterpriseGetEnterpriseEdgesResultItem.

        :param name: The name of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._name = name

    @property
    def operatorAlertsEnabled(self):
        """
        Gets the operatorAlertsEnabled of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The operatorAlertsEnabled of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: int
        """
        return self._operatorAlertsEnabled

    @operatorAlertsEnabled.setter
    def operatorAlertsEnabled(self, operatorAlertsEnabled):
        """
        Sets the operatorAlertsEnabled of this EnterpriseGetEnterpriseEdgesResultItem.

        :param operatorAlertsEnabled: The operatorAlertsEnabled of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: int
        """

        self._operatorAlertsEnabled = operatorAlertsEnabled

    @property
    def selfMacAddress(self):
        """
        Gets the selfMacAddress of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The selfMacAddress of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._selfMacAddress

    @selfMacAddress.setter
    def selfMacAddress(self, selfMacAddress):
        """
        Sets the selfMacAddress of this EnterpriseGetEnterpriseEdgesResultItem.

        :param selfMacAddress: The selfMacAddress of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._selfMacAddress = selfMacAddress

    @property
    def serialNumber(self):
        """
        Gets the serialNumber of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The serialNumber of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._serialNumber

    @serialNumber.setter
    def serialNumber(self, serialNumber):
        """
        Sets the serialNumber of this EnterpriseGetEnterpriseEdgesResultItem.

        :param serialNumber: The serialNumber of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._serialNumber = serialNumber

    @property
    def serviceState(self):
        """
        Gets the serviceState of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The serviceState of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._serviceState

    @serviceState.setter
    def serviceState(self, serviceState):
        """
        Sets the serviceState of this EnterpriseGetEnterpriseEdgesResultItem.

        :param serviceState: The serviceState of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._serviceState = serviceState

    @property
    def serviceUpSince(self):
        """
        Gets the serviceUpSince of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The serviceUpSince of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._serviceUpSince

    @serviceUpSince.setter
    def serviceUpSince(self, serviceUpSince):
        """
        Sets the serviceUpSince of this EnterpriseGetEnterpriseEdgesResultItem.

        :param serviceUpSince: The serviceUpSince of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._serviceUpSince = serviceUpSince

    @property
    def siteId(self):
        """
        Gets the siteId of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The siteId of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: int
        """
        return self._siteId

    @siteId.setter
    def siteId(self, siteId):
        """
        Sets the siteId of this EnterpriseGetEnterpriseEdgesResultItem.

        :param siteId: The siteId of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: int
        """

        self._siteId = siteId

    @property
    def softwareUpdated(self):
        """
        Gets the softwareUpdated of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The softwareUpdated of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._softwareUpdated

    @softwareUpdated.setter
    def softwareUpdated(self, softwareUpdated):
        """
        Sets the softwareUpdated of this EnterpriseGetEnterpriseEdgesResultItem.

        :param softwareUpdated: The softwareUpdated of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._softwareUpdated = softwareUpdated

    @property
    def softwareVersion(self):
        """
        Gets the softwareVersion of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The softwareVersion of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._softwareVersion

    @softwareVersion.setter
    def softwareVersion(self, softwareVersion):
        """
        Sets the softwareVersion of this EnterpriseGetEnterpriseEdgesResultItem.

        :param softwareVersion: The softwareVersion of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._softwareVersion = softwareVersion

    @property
    def systemUpSince(self):
        """
        Gets the systemUpSince of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The systemUpSince of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: str
        """
        return self._systemUpSince

    @systemUpSince.setter
    def systemUpSince(self, systemUpSince):
        """
        Sets the systemUpSince of this EnterpriseGetEnterpriseEdgesResultItem.

        :param systemUpSince: The systemUpSince of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: str
        """

        self._systemUpSince = systemUpSince

    @property
    def configuration(self):
        """
        Gets the configuration of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The configuration of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: ModelConfiguration
        """
        return self._configuration

    @configuration.setter
    def configuration(self, configuration):
        """
        Sets the configuration of this EnterpriseGetEnterpriseEdgesResultItem.

        :param configuration: The configuration of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: ModelConfiguration
        """

        self._configuration = configuration

    @property
    def links(self):
        """
        Gets the links of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The links of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: list[Link]
        """
        return self._links

    @links.setter
    def links(self, links):
        """
        Sets the links of this EnterpriseGetEnterpriseEdgesResultItem.

        :param links: The links of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: list[Link]
        """

        self._links = links

    @property
    def recentLinks(self):
        """
        Gets the recentLinks of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The recentLinks of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: list[Link]
        """
        return self._recentLinks

    @recentLinks.setter
    def recentLinks(self, recentLinks):
        """
        Sets the recentLinks of this EnterpriseGetEnterpriseEdgesResultItem.

        :param recentLinks: The recentLinks of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: list[Link]
        """

        self._recentLinks = recentLinks

    @property
    def site(self):
        """
        Gets the site of this EnterpriseGetEnterpriseEdgesResultItem.

        :return: The site of this EnterpriseGetEnterpriseEdgesResultItem.
        :rtype: Site
        """
        return self._site

    @site.setter
    def site(self, site):
        """
        Sets the site of this EnterpriseGetEnterpriseEdgesResultItem.

        :param site: The site of this EnterpriseGetEnterpriseEdgesResultItem.
        :type: Site
        """

        self._site = site

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
        if not isinstance(other, EnterpriseGetEnterpriseEdgesResultItem):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
