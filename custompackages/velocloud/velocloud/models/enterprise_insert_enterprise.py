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


class EnterpriseInsertEnterprise(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, city=None, contactEmail=None, contactMobile=None, contactName=None, contactPhone=None, country=None, lat=None, lon=None, name=None, postalCode=None, state=None, streetAddress=None, streetAddress2=None, gatewayPoolId=None, networkId=None, returnData=None, user=None, configurationId=None, enableEnterpriseDelegationToOperator=None, enableEnterpriseDelegationToProxy=None, enableEnterpriseUserManagementDelegationToOperator=None):
        """
        EnterpriseInsertEnterprise - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'city': 'str',
            'contactEmail': 'str',
            'contactMobile': 'str',
            'contactName': 'str',
            'contactPhone': 'str',
            'country': 'str',
            'lat': 'float',
            'lon': 'float',
            'name': 'str',
            'postalCode': 'str',
            'state': 'str',
            'streetAddress': 'str',
            'streetAddress2': 'str',
            'gatewayPoolId': 'int',
            'networkId': 'int',
            'returnData': 'bool',
            'user': 'AuthObject',
            'configurationId': 'int',
            'enableEnterpriseDelegationToOperator': 'bool',
            'enableEnterpriseDelegationToProxy': 'bool',
            'enableEnterpriseUserManagementDelegationToOperator': 'bool'
        }

        self.attribute_map = {
            'city': 'city',
            'contactEmail': 'contactEmail',
            'contactMobile': 'contactMobile',
            'contactName': 'contactName',
            'contactPhone': 'contactPhone',
            'country': 'country',
            'lat': 'lat',
            'lon': 'lon',
            'name': 'name',
            'postalCode': 'postalCode',
            'state': 'state',
            'streetAddress': 'streetAddress',
            'streetAddress2': 'streetAddress2',
            'gatewayPoolId': 'gatewayPoolId',
            'networkId': 'networkId',
            'returnData': 'returnData',
            'user': 'user',
            'configurationId': 'configurationId',
            'enableEnterpriseDelegationToOperator': 'enableEnterpriseDelegationToOperator',
            'enableEnterpriseDelegationToProxy': 'enableEnterpriseDelegationToProxy',
            'enableEnterpriseUserManagementDelegationToOperator': 'enableEnterpriseUserManagementDelegationToOperator'
        }

        self._city = city
        self._contactEmail = contactEmail
        self._contactMobile = contactMobile
        self._contactName = contactName
        self._contactPhone = contactPhone
        self._country = country
        self._lat = lat
        self._lon = lon
        self._name = name
        self._postalCode = postalCode
        self._state = state
        self._streetAddress = streetAddress
        self._streetAddress2 = streetAddress2
        self._gatewayPoolId = gatewayPoolId
        self._networkId = networkId
        self._returnData = returnData
        self._user = user
        self._configurationId = configurationId
        self._enableEnterpriseDelegationToOperator = enableEnterpriseDelegationToOperator
        self._enableEnterpriseDelegationToProxy = enableEnterpriseDelegationToProxy
        self._enableEnterpriseUserManagementDelegationToOperator = enableEnterpriseUserManagementDelegationToOperator

    @property
    def city(self):
        """
        Gets the city of this EnterpriseInsertEnterprise.

        :return: The city of this EnterpriseInsertEnterprise.
        :rtype: str
        """
        return self._city

    @city.setter
    def city(self, city):
        """
        Sets the city of this EnterpriseInsertEnterprise.

        :param city: The city of this EnterpriseInsertEnterprise.
        :type: str
        """

        self._city = city

    @property
    def contactEmail(self):
        """
        Gets the contactEmail of this EnterpriseInsertEnterprise.

        :return: The contactEmail of this EnterpriseInsertEnterprise.
        :rtype: str
        """
        return self._contactEmail

    @contactEmail.setter
    def contactEmail(self, contactEmail):
        """
        Sets the contactEmail of this EnterpriseInsertEnterprise.

        :param contactEmail: The contactEmail of this EnterpriseInsertEnterprise.
        :type: str
        """

        self._contactEmail = contactEmail

    @property
    def contactMobile(self):
        """
        Gets the contactMobile of this EnterpriseInsertEnterprise.

        :return: The contactMobile of this EnterpriseInsertEnterprise.
        :rtype: str
        """
        return self._contactMobile

    @contactMobile.setter
    def contactMobile(self, contactMobile):
        """
        Sets the contactMobile of this EnterpriseInsertEnterprise.

        :param contactMobile: The contactMobile of this EnterpriseInsertEnterprise.
        :type: str
        """

        self._contactMobile = contactMobile

    @property
    def contactName(self):
        """
        Gets the contactName of this EnterpriseInsertEnterprise.

        :return: The contactName of this EnterpriseInsertEnterprise.
        :rtype: str
        """
        return self._contactName

    @contactName.setter
    def contactName(self, contactName):
        """
        Sets the contactName of this EnterpriseInsertEnterprise.

        :param contactName: The contactName of this EnterpriseInsertEnterprise.
        :type: str
        """

        self._contactName = contactName

    @property
    def contactPhone(self):
        """
        Gets the contactPhone of this EnterpriseInsertEnterprise.

        :return: The contactPhone of this EnterpriseInsertEnterprise.
        :rtype: str
        """
        return self._contactPhone

    @contactPhone.setter
    def contactPhone(self, contactPhone):
        """
        Sets the contactPhone of this EnterpriseInsertEnterprise.

        :param contactPhone: The contactPhone of this EnterpriseInsertEnterprise.
        :type: str
        """

        self._contactPhone = contactPhone

    @property
    def country(self):
        """
        Gets the country of this EnterpriseInsertEnterprise.

        :return: The country of this EnterpriseInsertEnterprise.
        :rtype: str
        """
        return self._country

    @country.setter
    def country(self, country):
        """
        Sets the country of this EnterpriseInsertEnterprise.

        :param country: The country of this EnterpriseInsertEnterprise.
        :type: str
        """

        self._country = country

    @property
    def lat(self):
        """
        Gets the lat of this EnterpriseInsertEnterprise.

        :return: The lat of this EnterpriseInsertEnterprise.
        :rtype: float
        """
        return self._lat

    @lat.setter
    def lat(self, lat):
        """
        Sets the lat of this EnterpriseInsertEnterprise.

        :param lat: The lat of this EnterpriseInsertEnterprise.
        :type: float
        """

        self._lat = lat

    @property
    def lon(self):
        """
        Gets the lon of this EnterpriseInsertEnterprise.

        :return: The lon of this EnterpriseInsertEnterprise.
        :rtype: float
        """
        return self._lon

    @lon.setter
    def lon(self, lon):
        """
        Sets the lon of this EnterpriseInsertEnterprise.

        :param lon: The lon of this EnterpriseInsertEnterprise.
        :type: float
        """

        self._lon = lon

    @property
    def name(self):
        """
        Gets the name of this EnterpriseInsertEnterprise.

        :return: The name of this EnterpriseInsertEnterprise.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this EnterpriseInsertEnterprise.

        :param name: The name of this EnterpriseInsertEnterprise.
        :type: str
        """

        self._name = name

    @property
    def postalCode(self):
        """
        Gets the postalCode of this EnterpriseInsertEnterprise.

        :return: The postalCode of this EnterpriseInsertEnterprise.
        :rtype: str
        """
        return self._postalCode

    @postalCode.setter
    def postalCode(self, postalCode):
        """
        Sets the postalCode of this EnterpriseInsertEnterprise.

        :param postalCode: The postalCode of this EnterpriseInsertEnterprise.
        :type: str
        """

        self._postalCode = postalCode

    @property
    def state(self):
        """
        Gets the state of this EnterpriseInsertEnterprise.

        :return: The state of this EnterpriseInsertEnterprise.
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """
        Sets the state of this EnterpriseInsertEnterprise.

        :param state: The state of this EnterpriseInsertEnterprise.
        :type: str
        """

        self._state = state

    @property
    def streetAddress(self):
        """
        Gets the streetAddress of this EnterpriseInsertEnterprise.

        :return: The streetAddress of this EnterpriseInsertEnterprise.
        :rtype: str
        """
        return self._streetAddress

    @streetAddress.setter
    def streetAddress(self, streetAddress):
        """
        Sets the streetAddress of this EnterpriseInsertEnterprise.

        :param streetAddress: The streetAddress of this EnterpriseInsertEnterprise.
        :type: str
        """

        self._streetAddress = streetAddress

    @property
    def streetAddress2(self):
        """
        Gets the streetAddress2 of this EnterpriseInsertEnterprise.

        :return: The streetAddress2 of this EnterpriseInsertEnterprise.
        :rtype: str
        """
        return self._streetAddress2

    @streetAddress2.setter
    def streetAddress2(self, streetAddress2):
        """
        Sets the streetAddress2 of this EnterpriseInsertEnterprise.

        :param streetAddress2: The streetAddress2 of this EnterpriseInsertEnterprise.
        :type: str
        """

        self._streetAddress2 = streetAddress2

    @property
    def gatewayPoolId(self):
        """
        Gets the gatewayPoolId of this EnterpriseInsertEnterprise.

        :return: The gatewayPoolId of this EnterpriseInsertEnterprise.
        :rtype: int
        """
        return self._gatewayPoolId

    @gatewayPoolId.setter
    def gatewayPoolId(self, gatewayPoolId):
        """
        Sets the gatewayPoolId of this EnterpriseInsertEnterprise.

        :param gatewayPoolId: The gatewayPoolId of this EnterpriseInsertEnterprise.
        :type: int
        """

        self._gatewayPoolId = gatewayPoolId

    @property
    def networkId(self):
        """
        Gets the networkId of this EnterpriseInsertEnterprise.

        :return: The networkId of this EnterpriseInsertEnterprise.
        :rtype: int
        """
        return self._networkId

    @networkId.setter
    def networkId(self, networkId):
        """
        Sets the networkId of this EnterpriseInsertEnterprise.

        :param networkId: The networkId of this EnterpriseInsertEnterprise.
        :type: int
        """

        self._networkId = networkId

    @property
    def returnData(self):
        """
        Gets the returnData of this EnterpriseInsertEnterprise.

        :return: The returnData of this EnterpriseInsertEnterprise.
        :rtype: bool
        """
        return self._returnData

    @returnData.setter
    def returnData(self, returnData):
        """
        Sets the returnData of this EnterpriseInsertEnterprise.

        :param returnData: The returnData of this EnterpriseInsertEnterprise.
        :type: bool
        """

        self._returnData = returnData

    @property
    def user(self):
        """
        Gets the user of this EnterpriseInsertEnterprise.

        :return: The user of this EnterpriseInsertEnterprise.
        :rtype: AuthObject
        """
        return self._user

    @user.setter
    def user(self, user):
        """
        Sets the user of this EnterpriseInsertEnterprise.

        :param user: The user of this EnterpriseInsertEnterprise.
        :type: AuthObject
        """

        self._user = user

    @property
    def configurationId(self):
        """
        Gets the configurationId of this EnterpriseInsertEnterprise.

        :return: The configurationId of this EnterpriseInsertEnterprise.
        :rtype: int
        """
        return self._configurationId

    @configurationId.setter
    def configurationId(self, configurationId):
        """
        Sets the configurationId of this EnterpriseInsertEnterprise.

        :param configurationId: The configurationId of this EnterpriseInsertEnterprise.
        :type: int
        """

        self._configurationId = configurationId

    @property
    def enableEnterpriseDelegationToOperator(self):
        """
        Gets the enableEnterpriseDelegationToOperator of this EnterpriseInsertEnterprise.

        :return: The enableEnterpriseDelegationToOperator of this EnterpriseInsertEnterprise.
        :rtype: bool
        """
        return self._enableEnterpriseDelegationToOperator

    @enableEnterpriseDelegationToOperator.setter
    def enableEnterpriseDelegationToOperator(self, enableEnterpriseDelegationToOperator):
        """
        Sets the enableEnterpriseDelegationToOperator of this EnterpriseInsertEnterprise.

        :param enableEnterpriseDelegationToOperator: The enableEnterpriseDelegationToOperator of this EnterpriseInsertEnterprise.
        :type: bool
        """

        self._enableEnterpriseDelegationToOperator = enableEnterpriseDelegationToOperator

    @property
    def enableEnterpriseDelegationToProxy(self):
        """
        Gets the enableEnterpriseDelegationToProxy of this EnterpriseInsertEnterprise.

        :return: The enableEnterpriseDelegationToProxy of this EnterpriseInsertEnterprise.
        :rtype: bool
        """
        return self._enableEnterpriseDelegationToProxy

    @enableEnterpriseDelegationToProxy.setter
    def enableEnterpriseDelegationToProxy(self, enableEnterpriseDelegationToProxy):
        """
        Sets the enableEnterpriseDelegationToProxy of this EnterpriseInsertEnterprise.

        :param enableEnterpriseDelegationToProxy: The enableEnterpriseDelegationToProxy of this EnterpriseInsertEnterprise.
        :type: bool
        """

        self._enableEnterpriseDelegationToProxy = enableEnterpriseDelegationToProxy

    @property
    def enableEnterpriseUserManagementDelegationToOperator(self):
        """
        Gets the enableEnterpriseUserManagementDelegationToOperator of this EnterpriseInsertEnterprise.

        :return: The enableEnterpriseUserManagementDelegationToOperator of this EnterpriseInsertEnterprise.
        :rtype: bool
        """
        return self._enableEnterpriseUserManagementDelegationToOperator

    @enableEnterpriseUserManagementDelegationToOperator.setter
    def enableEnterpriseUserManagementDelegationToOperator(self, enableEnterpriseUserManagementDelegationToOperator):
        """
        Sets the enableEnterpriseUserManagementDelegationToOperator of this EnterpriseInsertEnterprise.

        :param enableEnterpriseUserManagementDelegationToOperator: The enableEnterpriseUserManagementDelegationToOperator of this EnterpriseInsertEnterprise.
        :type: bool
        """

        self._enableEnterpriseUserManagementDelegationToOperator = enableEnterpriseUserManagementDelegationToOperator

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
        if not isinstance(other, EnterpriseInsertEnterprise):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
