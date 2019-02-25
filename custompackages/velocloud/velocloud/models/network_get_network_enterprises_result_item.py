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


class NetworkGetNetworkEnterprisesResultItem(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, id=None, created=None, networkId=None, gatewayPoolId=None, alertsEnabled=None, operatorAlertsEnabled=None, endpointPkiMode=None, name=None, domain=None, prefix=None, logicalId=None, accountNumber=None, description=None, contactName=None, contactPhone=None, contactMobile=None, contactEmail=None, streetAddress=None, streetAddress2=None, city=None, state=None, postalCode=None, country=None, lat=None, lon=None, timezone=None, locale=None, modified=None, enterpriseProxyId=None, enterpriseProxyName=None, edgeCount=None, edges=None, edgeConfigUpdate=None):
        """
        NetworkGetNetworkEnterprisesResultItem - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'int',
            'created': 'datetime',
            'networkId': 'int',
            'gatewayPoolId': 'int',
            'alertsEnabled': 'bool',
            'operatorAlertsEnabled': 'bool',
            'endpointPkiMode': 'str',
            'name': 'str',
            'domain': 'str',
            'prefix': 'str',
            'logicalId': 'str',
            'accountNumber': 'str',
            'description': 'str',
            'contactName': 'str',
            'contactPhone': 'str',
            'contactMobile': 'str',
            'contactEmail': 'str',
            'streetAddress': 'str',
            'streetAddress2': 'str',
            'city': 'str',
            'state': 'str',
            'postalCode': 'str',
            'country': 'str',
            'lat': 'float',
            'lon': 'float',
            'timezone': 'str',
            'locale': 'str',
            'modified': 'datetime',
            'enterpriseProxyId': 'int',
            'enterpriseProxyName': 'str',
            'edgeCount': 'int',
            'edges': 'list[EdgeObject]',
            'edgeConfigUpdate': 'NetworkGetNetworkEnterprisesResultItemEdgeConfigUpdate'
        }

        self.attribute_map = {
            'id': 'id',
            'created': 'created',
            'networkId': 'networkId',
            'gatewayPoolId': 'gatewayPoolId',
            'alertsEnabled': 'alertsEnabled',
            'operatorAlertsEnabled': 'operatorAlertsEnabled',
            'endpointPkiMode': 'endpointPkiMode',
            'name': 'name',
            'domain': 'domain',
            'prefix': 'prefix',
            'logicalId': 'logicalId',
            'accountNumber': 'accountNumber',
            'description': 'description',
            'contactName': 'contactName',
            'contactPhone': 'contactPhone',
            'contactMobile': 'contactMobile',
            'contactEmail': 'contactEmail',
            'streetAddress': 'streetAddress',
            'streetAddress2': 'streetAddress2',
            'city': 'city',
            'state': 'state',
            'postalCode': 'postalCode',
            'country': 'country',
            'lat': 'lat',
            'lon': 'lon',
            'timezone': 'timezone',
            'locale': 'locale',
            'modified': 'modified',
            'enterpriseProxyId': 'enterpriseProxyId',
            'enterpriseProxyName': 'enterpriseProxyName',
            'edgeCount': 'edgeCount',
            'edges': 'edges',
            'edgeConfigUpdate': 'edgeConfigUpdate'
        }

        self._id = id
        self._created = created
        self._networkId = networkId
        self._gatewayPoolId = gatewayPoolId
        self._alertsEnabled = alertsEnabled
        self._operatorAlertsEnabled = operatorAlertsEnabled
        self._endpointPkiMode = endpointPkiMode
        self._name = name
        self._domain = domain
        self._prefix = prefix
        self._logicalId = logicalId
        self._accountNumber = accountNumber
        self._description = description
        self._contactName = contactName
        self._contactPhone = contactPhone
        self._contactMobile = contactMobile
        self._contactEmail = contactEmail
        self._streetAddress = streetAddress
        self._streetAddress2 = streetAddress2
        self._city = city
        self._state = state
        self._postalCode = postalCode
        self._country = country
        self._lat = lat
        self._lon = lon
        self._timezone = timezone
        self._locale = locale
        self._modified = modified
        self._enterpriseProxyId = enterpriseProxyId
        self._enterpriseProxyName = enterpriseProxyName
        self._edgeCount = edgeCount
        self._edges = edges
        self._edgeConfigUpdate = edgeConfigUpdate

    @property
    def id(self):
        """
        Gets the id of this NetworkGetNetworkEnterprisesResultItem.

        :return: The id of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this NetworkGetNetworkEnterprisesResultItem.

        :param id: The id of this NetworkGetNetworkEnterprisesResultItem.
        :type: int
        """

        self._id = id

    @property
    def created(self):
        """
        Gets the created of this NetworkGetNetworkEnterprisesResultItem.

        :return: The created of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: datetime
        """
        return self._created

    @created.setter
    def created(self, created):
        """
        Sets the created of this NetworkGetNetworkEnterprisesResultItem.

        :param created: The created of this NetworkGetNetworkEnterprisesResultItem.
        :type: datetime
        """

        self._created = created

    @property
    def networkId(self):
        """
        Gets the networkId of this NetworkGetNetworkEnterprisesResultItem.

        :return: The networkId of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: int
        """
        return self._networkId

    @networkId.setter
    def networkId(self, networkId):
        """
        Sets the networkId of this NetworkGetNetworkEnterprisesResultItem.

        :param networkId: The networkId of this NetworkGetNetworkEnterprisesResultItem.
        :type: int
        """

        self._networkId = networkId

    @property
    def gatewayPoolId(self):
        """
        Gets the gatewayPoolId of this NetworkGetNetworkEnterprisesResultItem.

        :return: The gatewayPoolId of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: int
        """
        return self._gatewayPoolId

    @gatewayPoolId.setter
    def gatewayPoolId(self, gatewayPoolId):
        """
        Sets the gatewayPoolId of this NetworkGetNetworkEnterprisesResultItem.

        :param gatewayPoolId: The gatewayPoolId of this NetworkGetNetworkEnterprisesResultItem.
        :type: int
        """

        self._gatewayPoolId = gatewayPoolId

    @property
    def alertsEnabled(self):
        """
        Gets the alertsEnabled of this NetworkGetNetworkEnterprisesResultItem.

        :return: The alertsEnabled of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: bool
        """
        return self._alertsEnabled

    @alertsEnabled.setter
    def alertsEnabled(self, alertsEnabled):
        """
        Sets the alertsEnabled of this NetworkGetNetworkEnterprisesResultItem.

        :param alertsEnabled: The alertsEnabled of this NetworkGetNetworkEnterprisesResultItem.
        :type: bool
        """

        self._alertsEnabled = alertsEnabled

    @property
    def operatorAlertsEnabled(self):
        """
        Gets the operatorAlertsEnabled of this NetworkGetNetworkEnterprisesResultItem.

        :return: The operatorAlertsEnabled of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: bool
        """
        return self._operatorAlertsEnabled

    @operatorAlertsEnabled.setter
    def operatorAlertsEnabled(self, operatorAlertsEnabled):
        """
        Sets the operatorAlertsEnabled of this NetworkGetNetworkEnterprisesResultItem.

        :param operatorAlertsEnabled: The operatorAlertsEnabled of this NetworkGetNetworkEnterprisesResultItem.
        :type: bool
        """

        self._operatorAlertsEnabled = operatorAlertsEnabled

    @property
    def endpointPkiMode(self):
        """
        Gets the endpointPkiMode of this NetworkGetNetworkEnterprisesResultItem.

        :return: The endpointPkiMode of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._endpointPkiMode

    @endpointPkiMode.setter
    def endpointPkiMode(self, endpointPkiMode):
        """
        Sets the endpointPkiMode of this NetworkGetNetworkEnterprisesResultItem.

        :param endpointPkiMode: The endpointPkiMode of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._endpointPkiMode = endpointPkiMode

    @property
    def name(self):
        """
        Gets the name of this NetworkGetNetworkEnterprisesResultItem.

        :return: The name of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this NetworkGetNetworkEnterprisesResultItem.

        :param name: The name of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._name = name

    @property
    def domain(self):
        """
        Gets the domain of this NetworkGetNetworkEnterprisesResultItem.

        :return: The domain of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._domain

    @domain.setter
    def domain(self, domain):
        """
        Sets the domain of this NetworkGetNetworkEnterprisesResultItem.

        :param domain: The domain of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._domain = domain

    @property
    def prefix(self):
        """
        Gets the prefix of this NetworkGetNetworkEnterprisesResultItem.

        :return: The prefix of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._prefix

    @prefix.setter
    def prefix(self, prefix):
        """
        Sets the prefix of this NetworkGetNetworkEnterprisesResultItem.

        :param prefix: The prefix of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._prefix = prefix

    @property
    def logicalId(self):
        """
        Gets the logicalId of this NetworkGetNetworkEnterprisesResultItem.

        :return: The logicalId of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._logicalId

    @logicalId.setter
    def logicalId(self, logicalId):
        """
        Sets the logicalId of this NetworkGetNetworkEnterprisesResultItem.

        :param logicalId: The logicalId of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._logicalId = logicalId

    @property
    def accountNumber(self):
        """
        Gets the accountNumber of this NetworkGetNetworkEnterprisesResultItem.

        :return: The accountNumber of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._accountNumber

    @accountNumber.setter
    def accountNumber(self, accountNumber):
        """
        Sets the accountNumber of this NetworkGetNetworkEnterprisesResultItem.

        :param accountNumber: The accountNumber of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._accountNumber = accountNumber

    @property
    def description(self):
        """
        Gets the description of this NetworkGetNetworkEnterprisesResultItem.

        :return: The description of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this NetworkGetNetworkEnterprisesResultItem.

        :param description: The description of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._description = description

    @property
    def contactName(self):
        """
        Gets the contactName of this NetworkGetNetworkEnterprisesResultItem.

        :return: The contactName of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._contactName

    @contactName.setter
    def contactName(self, contactName):
        """
        Sets the contactName of this NetworkGetNetworkEnterprisesResultItem.

        :param contactName: The contactName of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._contactName = contactName

    @property
    def contactPhone(self):
        """
        Gets the contactPhone of this NetworkGetNetworkEnterprisesResultItem.

        :return: The contactPhone of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._contactPhone

    @contactPhone.setter
    def contactPhone(self, contactPhone):
        """
        Sets the contactPhone of this NetworkGetNetworkEnterprisesResultItem.

        :param contactPhone: The contactPhone of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._contactPhone = contactPhone

    @property
    def contactMobile(self):
        """
        Gets the contactMobile of this NetworkGetNetworkEnterprisesResultItem.

        :return: The contactMobile of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._contactMobile

    @contactMobile.setter
    def contactMobile(self, contactMobile):
        """
        Sets the contactMobile of this NetworkGetNetworkEnterprisesResultItem.

        :param contactMobile: The contactMobile of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._contactMobile = contactMobile

    @property
    def contactEmail(self):
        """
        Gets the contactEmail of this NetworkGetNetworkEnterprisesResultItem.

        :return: The contactEmail of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._contactEmail

    @contactEmail.setter
    def contactEmail(self, contactEmail):
        """
        Sets the contactEmail of this NetworkGetNetworkEnterprisesResultItem.

        :param contactEmail: The contactEmail of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._contactEmail = contactEmail

    @property
    def streetAddress(self):
        """
        Gets the streetAddress of this NetworkGetNetworkEnterprisesResultItem.

        :return: The streetAddress of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._streetAddress

    @streetAddress.setter
    def streetAddress(self, streetAddress):
        """
        Sets the streetAddress of this NetworkGetNetworkEnterprisesResultItem.

        :param streetAddress: The streetAddress of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._streetAddress = streetAddress

    @property
    def streetAddress2(self):
        """
        Gets the streetAddress2 of this NetworkGetNetworkEnterprisesResultItem.

        :return: The streetAddress2 of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._streetAddress2

    @streetAddress2.setter
    def streetAddress2(self, streetAddress2):
        """
        Sets the streetAddress2 of this NetworkGetNetworkEnterprisesResultItem.

        :param streetAddress2: The streetAddress2 of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._streetAddress2 = streetAddress2

    @property
    def city(self):
        """
        Gets the city of this NetworkGetNetworkEnterprisesResultItem.

        :return: The city of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._city

    @city.setter
    def city(self, city):
        """
        Sets the city of this NetworkGetNetworkEnterprisesResultItem.

        :param city: The city of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._city = city

    @property
    def state(self):
        """
        Gets the state of this NetworkGetNetworkEnterprisesResultItem.

        :return: The state of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """
        Sets the state of this NetworkGetNetworkEnterprisesResultItem.

        :param state: The state of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._state = state

    @property
    def postalCode(self):
        """
        Gets the postalCode of this NetworkGetNetworkEnterprisesResultItem.

        :return: The postalCode of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._postalCode

    @postalCode.setter
    def postalCode(self, postalCode):
        """
        Sets the postalCode of this NetworkGetNetworkEnterprisesResultItem.

        :param postalCode: The postalCode of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._postalCode = postalCode

    @property
    def country(self):
        """
        Gets the country of this NetworkGetNetworkEnterprisesResultItem.

        :return: The country of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._country

    @country.setter
    def country(self, country):
        """
        Sets the country of this NetworkGetNetworkEnterprisesResultItem.

        :param country: The country of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._country = country

    @property
    def lat(self):
        """
        Gets the lat of this NetworkGetNetworkEnterprisesResultItem.

        :return: The lat of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: float
        """
        return self._lat

    @lat.setter
    def lat(self, lat):
        """
        Sets the lat of this NetworkGetNetworkEnterprisesResultItem.

        :param lat: The lat of this NetworkGetNetworkEnterprisesResultItem.
        :type: float
        """

        self._lat = lat

    @property
    def lon(self):
        """
        Gets the lon of this NetworkGetNetworkEnterprisesResultItem.

        :return: The lon of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: float
        """
        return self._lon

    @lon.setter
    def lon(self, lon):
        """
        Sets the lon of this NetworkGetNetworkEnterprisesResultItem.

        :param lon: The lon of this NetworkGetNetworkEnterprisesResultItem.
        :type: float
        """

        self._lon = lon

    @property
    def timezone(self):
        """
        Gets the timezone of this NetworkGetNetworkEnterprisesResultItem.

        :return: The timezone of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._timezone

    @timezone.setter
    def timezone(self, timezone):
        """
        Sets the timezone of this NetworkGetNetworkEnterprisesResultItem.

        :param timezone: The timezone of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._timezone = timezone

    @property
    def locale(self):
        """
        Gets the locale of this NetworkGetNetworkEnterprisesResultItem.

        :return: The locale of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._locale

    @locale.setter
    def locale(self, locale):
        """
        Sets the locale of this NetworkGetNetworkEnterprisesResultItem.

        :param locale: The locale of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._locale = locale

    @property
    def modified(self):
        """
        Gets the modified of this NetworkGetNetworkEnterprisesResultItem.

        :return: The modified of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: datetime
        """
        return self._modified

    @modified.setter
    def modified(self, modified):
        """
        Sets the modified of this NetworkGetNetworkEnterprisesResultItem.

        :param modified: The modified of this NetworkGetNetworkEnterprisesResultItem.
        :type: datetime
        """

        self._modified = modified

    @property
    def enterpriseProxyId(self):
        """
        Gets the enterpriseProxyId of this NetworkGetNetworkEnterprisesResultItem.

        :return: The enterpriseProxyId of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: int
        """
        return self._enterpriseProxyId

    @enterpriseProxyId.setter
    def enterpriseProxyId(self, enterpriseProxyId):
        """
        Sets the enterpriseProxyId of this NetworkGetNetworkEnterprisesResultItem.

        :param enterpriseProxyId: The enterpriseProxyId of this NetworkGetNetworkEnterprisesResultItem.
        :type: int
        """

        self._enterpriseProxyId = enterpriseProxyId

    @property
    def enterpriseProxyName(self):
        """
        Gets the enterpriseProxyName of this NetworkGetNetworkEnterprisesResultItem.

        :return: The enterpriseProxyName of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: str
        """
        return self._enterpriseProxyName

    @enterpriseProxyName.setter
    def enterpriseProxyName(self, enterpriseProxyName):
        """
        Sets the enterpriseProxyName of this NetworkGetNetworkEnterprisesResultItem.

        :param enterpriseProxyName: The enterpriseProxyName of this NetworkGetNetworkEnterprisesResultItem.
        :type: str
        """

        self._enterpriseProxyName = enterpriseProxyName

    @property
    def edgeCount(self):
        """
        Gets the edgeCount of this NetworkGetNetworkEnterprisesResultItem.

        :return: The edgeCount of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: int
        """
        return self._edgeCount

    @edgeCount.setter
    def edgeCount(self, edgeCount):
        """
        Sets the edgeCount of this NetworkGetNetworkEnterprisesResultItem.

        :param edgeCount: The edgeCount of this NetworkGetNetworkEnterprisesResultItem.
        :type: int
        """

        self._edgeCount = edgeCount

    @property
    def edges(self):
        """
        Gets the edges of this NetworkGetNetworkEnterprisesResultItem.

        :return: The edges of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: list[EdgeObject]
        """
        return self._edges

    @edges.setter
    def edges(self, edges):
        """
        Sets the edges of this NetworkGetNetworkEnterprisesResultItem.

        :param edges: The edges of this NetworkGetNetworkEnterprisesResultItem.
        :type: list[EdgeObject]
        """

        self._edges = edges

    @property
    def edgeConfigUpdate(self):
        """
        Gets the edgeConfigUpdate of this NetworkGetNetworkEnterprisesResultItem.

        :return: The edgeConfigUpdate of this NetworkGetNetworkEnterprisesResultItem.
        :rtype: NetworkGetNetworkEnterprisesResultItemEdgeConfigUpdate
        """
        return self._edgeConfigUpdate

    @edgeConfigUpdate.setter
    def edgeConfigUpdate(self, edgeConfigUpdate):
        """
        Sets the edgeConfigUpdate of this NetworkGetNetworkEnterprisesResultItem.

        :param edgeConfigUpdate: The edgeConfigUpdate of this NetworkGetNetworkEnterprisesResultItem.
        :type: NetworkGetNetworkEnterprisesResultItemEdgeConfigUpdate
        """

        self._edgeConfigUpdate = edgeConfigUpdate

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
        if not isinstance(other, NetworkGetNetworkEnterprisesResultItem):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
