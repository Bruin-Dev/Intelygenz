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


class EnterpriseAlertConfiguration(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, id=None, created=None, alertDefinitionId=None, enterpriseId=None, enabled=None, name=None, description=None, type=None, definition=None, firstNotificationSeconds=None, maxNotifications=None, notificationIntervalSeconds=None, resetIntervalSeconds=None, modified=None):
        """
        EnterpriseAlertConfiguration - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'int',
            'created': 'datetime',
            'alertDefinitionId': 'int',
            'enterpriseId': 'int',
            'enabled': 'bool',
            'name': 'str',
            'description': 'str',
            'type': 'str',
            'definition': 'EnterpriseAlertDefinition',
            'firstNotificationSeconds': 'int',
            'maxNotifications': 'int',
            'notificationIntervalSeconds': 'int',
            'resetIntervalSeconds': 'int',
            'modified': 'datetime'
        }

        self.attribute_map = {
            'id': 'id',
            'created': 'created',
            'alertDefinitionId': 'alertDefinitionId',
            'enterpriseId': 'enterpriseId',
            'enabled': 'enabled',
            'name': 'name',
            'description': 'description',
            'type': 'type',
            'definition': 'definition',
            'firstNotificationSeconds': 'firstNotificationSeconds',
            'maxNotifications': 'maxNotifications',
            'notificationIntervalSeconds': 'notificationIntervalSeconds',
            'resetIntervalSeconds': 'resetIntervalSeconds',
            'modified': 'modified'
        }

        self._id = id
        self._created = created
        self._alertDefinitionId = alertDefinitionId
        self._enterpriseId = enterpriseId
        self._enabled = enabled
        self._name = name
        self._description = description
        self._type = type
        self._definition = definition
        self._firstNotificationSeconds = firstNotificationSeconds
        self._maxNotifications = maxNotifications
        self._notificationIntervalSeconds = notificationIntervalSeconds
        self._resetIntervalSeconds = resetIntervalSeconds
        self._modified = modified

    @property
    def id(self):
        """
        Gets the id of this EnterpriseAlertConfiguration.

        :return: The id of this EnterpriseAlertConfiguration.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this EnterpriseAlertConfiguration.

        :param id: The id of this EnterpriseAlertConfiguration.
        :type: int
        """

        self._id = id

    @property
    def created(self):
        """
        Gets the created of this EnterpriseAlertConfiguration.

        :return: The created of this EnterpriseAlertConfiguration.
        :rtype: datetime
        """
        return self._created

    @created.setter
    def created(self, created):
        """
        Sets the created of this EnterpriseAlertConfiguration.

        :param created: The created of this EnterpriseAlertConfiguration.
        :type: datetime
        """

        self._created = created

    @property
    def alertDefinitionId(self):
        """
        Gets the alertDefinitionId of this EnterpriseAlertConfiguration.

        :return: The alertDefinitionId of this EnterpriseAlertConfiguration.
        :rtype: int
        """
        return self._alertDefinitionId

    @alertDefinitionId.setter
    def alertDefinitionId(self, alertDefinitionId):
        """
        Sets the alertDefinitionId of this EnterpriseAlertConfiguration.

        :param alertDefinitionId: The alertDefinitionId of this EnterpriseAlertConfiguration.
        :type: int
        """

        self._alertDefinitionId = alertDefinitionId

    @property
    def enterpriseId(self):
        """
        Gets the enterpriseId of this EnterpriseAlertConfiguration.

        :return: The enterpriseId of this EnterpriseAlertConfiguration.
        :rtype: int
        """
        return self._enterpriseId

    @enterpriseId.setter
    def enterpriseId(self, enterpriseId):
        """
        Sets the enterpriseId of this EnterpriseAlertConfiguration.

        :param enterpriseId: The enterpriseId of this EnterpriseAlertConfiguration.
        :type: int
        """

        self._enterpriseId = enterpriseId

    @property
    def enabled(self):
        """
        Gets the enabled of this EnterpriseAlertConfiguration.

        :return: The enabled of this EnterpriseAlertConfiguration.
        :rtype: bool
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        """
        Sets the enabled of this EnterpriseAlertConfiguration.

        :param enabled: The enabled of this EnterpriseAlertConfiguration.
        :type: bool
        """

        self._enabled = enabled

    @property
    def name(self):
        """
        Gets the name of this EnterpriseAlertConfiguration.

        :return: The name of this EnterpriseAlertConfiguration.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this EnterpriseAlertConfiguration.

        :param name: The name of this EnterpriseAlertConfiguration.
        :type: str
        """

        self._name = name

    @property
    def description(self):
        """
        Gets the description of this EnterpriseAlertConfiguration.

        :return: The description of this EnterpriseAlertConfiguration.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this EnterpriseAlertConfiguration.

        :param description: The description of this EnterpriseAlertConfiguration.
        :type: str
        """

        self._description = description

    @property
    def type(self):
        """
        Gets the type of this EnterpriseAlertConfiguration.

        :return: The type of this EnterpriseAlertConfiguration.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        Sets the type of this EnterpriseAlertConfiguration.

        :param type: The type of this EnterpriseAlertConfiguration.
        :type: str
        """

        self._type = type

    @property
    def definition(self):
        """
        Gets the definition of this EnterpriseAlertConfiguration.

        :return: The definition of this EnterpriseAlertConfiguration.
        :rtype: EnterpriseAlertDefinition
        """
        return self._definition

    @definition.setter
    def definition(self, definition):
        """
        Sets the definition of this EnterpriseAlertConfiguration.

        :param definition: The definition of this EnterpriseAlertConfiguration.
        :type: EnterpriseAlertDefinition
        """

        self._definition = definition

    @property
    def firstNotificationSeconds(self):
        """
        Gets the firstNotificationSeconds of this EnterpriseAlertConfiguration.

        :return: The firstNotificationSeconds of this EnterpriseAlertConfiguration.
        :rtype: int
        """
        return self._firstNotificationSeconds

    @firstNotificationSeconds.setter
    def firstNotificationSeconds(self, firstNotificationSeconds):
        """
        Sets the firstNotificationSeconds of this EnterpriseAlertConfiguration.

        :param firstNotificationSeconds: The firstNotificationSeconds of this EnterpriseAlertConfiguration.
        :type: int
        """

        self._firstNotificationSeconds = firstNotificationSeconds

    @property
    def maxNotifications(self):
        """
        Gets the maxNotifications of this EnterpriseAlertConfiguration.

        :return: The maxNotifications of this EnterpriseAlertConfiguration.
        :rtype: int
        """
        return self._maxNotifications

    @maxNotifications.setter
    def maxNotifications(self, maxNotifications):
        """
        Sets the maxNotifications of this EnterpriseAlertConfiguration.

        :param maxNotifications: The maxNotifications of this EnterpriseAlertConfiguration.
        :type: int
        """

        self._maxNotifications = maxNotifications

    @property
    def notificationIntervalSeconds(self):
        """
        Gets the notificationIntervalSeconds of this EnterpriseAlertConfiguration.

        :return: The notificationIntervalSeconds of this EnterpriseAlertConfiguration.
        :rtype: int
        """
        return self._notificationIntervalSeconds

    @notificationIntervalSeconds.setter
    def notificationIntervalSeconds(self, notificationIntervalSeconds):
        """
        Sets the notificationIntervalSeconds of this EnterpriseAlertConfiguration.

        :param notificationIntervalSeconds: The notificationIntervalSeconds of this EnterpriseAlertConfiguration.
        :type: int
        """

        self._notificationIntervalSeconds = notificationIntervalSeconds

    @property
    def resetIntervalSeconds(self):
        """
        Gets the resetIntervalSeconds of this EnterpriseAlertConfiguration.

        :return: The resetIntervalSeconds of this EnterpriseAlertConfiguration.
        :rtype: int
        """
        return self._resetIntervalSeconds

    @resetIntervalSeconds.setter
    def resetIntervalSeconds(self, resetIntervalSeconds):
        """
        Sets the resetIntervalSeconds of this EnterpriseAlertConfiguration.

        :param resetIntervalSeconds: The resetIntervalSeconds of this EnterpriseAlertConfiguration.
        :type: int
        """

        self._resetIntervalSeconds = resetIntervalSeconds

    @property
    def modified(self):
        """
        Gets the modified of this EnterpriseAlertConfiguration.

        :return: The modified of this EnterpriseAlertConfiguration.
        :rtype: datetime
        """
        return self._modified

    @modified.setter
    def modified(self, modified):
        """
        Sets the modified of this EnterpriseAlertConfiguration.

        :param modified: The modified of this EnterpriseAlertConfiguration.
        :type: datetime
        """

        self._modified = modified

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
        if not isinstance(other, EnterpriseAlertConfiguration):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
