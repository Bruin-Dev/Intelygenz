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


class EnterpriseGetEnterpriseAlertsResultItem(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, id=None, created=None, triggerTime=None, enterpriseAlertConfigurationId=None, enterpriseId=None, edgeId=None, edgeName=None, linkId=None, linkName=None, enterpriseObjectId=None, enterpriseObjectName=None, name=None, type=None, state=None, stateSetTime=None, lastContact=None, firstNotificationSeconds=None, maxNotifications=None, notificationIntervalSeconds=None, resetIntervalSeconds=None, comment=None, nextNotificationTime=None, remainingNotifications=None, timezone=None, locale=None, modified=None):
        """
        EnterpriseGetEnterpriseAlertsResultItem - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'int',
            'created': 'datetime',
            'triggerTime': 'datetime',
            'enterpriseAlertConfigurationId': 'int',
            'enterpriseId': 'int',
            'edgeId': 'int',
            'edgeName': 'str',
            'linkId': 'int',
            'linkName': 'str',
            'enterpriseObjectId': 'int',
            'enterpriseObjectName': 'str',
            'name': 'str',
            'type': 'str',
            'state': 'str',
            'stateSetTime': 'datetime',
            'lastContact': 'datetime',
            'firstNotificationSeconds': 'int',
            'maxNotifications': 'int',
            'notificationIntervalSeconds': 'int',
            'resetIntervalSeconds': 'int',
            'comment': 'str',
            'nextNotificationTime': 'datetime',
            'remainingNotifications': 'int',
            'timezone': 'str',
            'locale': 'str',
            'modified': 'datetime'
        }

        self.attribute_map = {
            'id': 'id',
            'created': 'created',
            'triggerTime': 'triggerTime',
            'enterpriseAlertConfigurationId': 'enterpriseAlertConfigurationId',
            'enterpriseId': 'enterpriseId',
            'edgeId': 'edgeId',
            'edgeName': 'edgeName',
            'linkId': 'linkId',
            'linkName': 'linkName',
            'enterpriseObjectId': 'enterpriseObjectId',
            'enterpriseObjectName': 'enterpriseObjectName',
            'name': 'name',
            'type': 'type',
            'state': 'state',
            'stateSetTime': 'stateSetTime',
            'lastContact': 'lastContact',
            'firstNotificationSeconds': 'firstNotificationSeconds',
            'maxNotifications': 'maxNotifications',
            'notificationIntervalSeconds': 'notificationIntervalSeconds',
            'resetIntervalSeconds': 'resetIntervalSeconds',
            'comment': 'comment',
            'nextNotificationTime': 'nextNotificationTime',
            'remainingNotifications': 'remainingNotifications',
            'timezone': 'timezone',
            'locale': 'locale',
            'modified': 'modified'
        }

        self._id = id
        self._created = created
        self._triggerTime = triggerTime
        self._enterpriseAlertConfigurationId = enterpriseAlertConfigurationId
        self._enterpriseId = enterpriseId
        self._edgeId = edgeId
        self._edgeName = edgeName
        self._linkId = linkId
        self._linkName = linkName
        self._enterpriseObjectId = enterpriseObjectId
        self._enterpriseObjectName = enterpriseObjectName
        self._name = name
        self._type = type
        self._state = state
        self._stateSetTime = stateSetTime
        self._lastContact = lastContact
        self._firstNotificationSeconds = firstNotificationSeconds
        self._maxNotifications = maxNotifications
        self._notificationIntervalSeconds = notificationIntervalSeconds
        self._resetIntervalSeconds = resetIntervalSeconds
        self._comment = comment
        self._nextNotificationTime = nextNotificationTime
        self._remainingNotifications = remainingNotifications
        self._timezone = timezone
        self._locale = locale
        self._modified = modified

    @property
    def id(self):
        """
        Gets the id of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The id of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this EnterpriseGetEnterpriseAlertsResultItem.

        :param id: The id of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: int
        """

        self._id = id

    @property
    def created(self):
        """
        Gets the created of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The created of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: datetime
        """
        return self._created

    @created.setter
    def created(self, created):
        """
        Sets the created of this EnterpriseGetEnterpriseAlertsResultItem.

        :param created: The created of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: datetime
        """

        self._created = created

    @property
    def triggerTime(self):
        """
        Gets the triggerTime of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The triggerTime of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: datetime
        """
        return self._triggerTime

    @triggerTime.setter
    def triggerTime(self, triggerTime):
        """
        Sets the triggerTime of this EnterpriseGetEnterpriseAlertsResultItem.

        :param triggerTime: The triggerTime of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: datetime
        """

        self._triggerTime = triggerTime

    @property
    def enterpriseAlertConfigurationId(self):
        """
        Gets the enterpriseAlertConfigurationId of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The enterpriseAlertConfigurationId of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: int
        """
        return self._enterpriseAlertConfigurationId

    @enterpriseAlertConfigurationId.setter
    def enterpriseAlertConfigurationId(self, enterpriseAlertConfigurationId):
        """
        Sets the enterpriseAlertConfigurationId of this EnterpriseGetEnterpriseAlertsResultItem.

        :param enterpriseAlertConfigurationId: The enterpriseAlertConfigurationId of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: int
        """

        self._enterpriseAlertConfigurationId = enterpriseAlertConfigurationId

    @property
    def enterpriseId(self):
        """
        Gets the enterpriseId of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The enterpriseId of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: int
        """
        return self._enterpriseId

    @enterpriseId.setter
    def enterpriseId(self, enterpriseId):
        """
        Sets the enterpriseId of this EnterpriseGetEnterpriseAlertsResultItem.

        :param enterpriseId: The enterpriseId of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: int
        """

        self._enterpriseId = enterpriseId

    @property
    def edgeId(self):
        """
        Gets the edgeId of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The edgeId of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: int
        """
        return self._edgeId

    @edgeId.setter
    def edgeId(self, edgeId):
        """
        Sets the edgeId of this EnterpriseGetEnterpriseAlertsResultItem.

        :param edgeId: The edgeId of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: int
        """

        self._edgeId = edgeId

    @property
    def edgeName(self):
        """
        Gets the edgeName of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The edgeName of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: str
        """
        return self._edgeName

    @edgeName.setter
    def edgeName(self, edgeName):
        """
        Sets the edgeName of this EnterpriseGetEnterpriseAlertsResultItem.

        :param edgeName: The edgeName of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: str
        """

        self._edgeName = edgeName

    @property
    def linkId(self):
        """
        Gets the linkId of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The linkId of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: int
        """
        return self._linkId

    @linkId.setter
    def linkId(self, linkId):
        """
        Sets the linkId of this EnterpriseGetEnterpriseAlertsResultItem.

        :param linkId: The linkId of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: int
        """

        self._linkId = linkId

    @property
    def linkName(self):
        """
        Gets the linkName of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The linkName of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: str
        """
        return self._linkName

    @linkName.setter
    def linkName(self, linkName):
        """
        Sets the linkName of this EnterpriseGetEnterpriseAlertsResultItem.

        :param linkName: The linkName of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: str
        """

        self._linkName = linkName

    @property
    def enterpriseObjectId(self):
        """
        Gets the enterpriseObjectId of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The enterpriseObjectId of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: int
        """
        return self._enterpriseObjectId

    @enterpriseObjectId.setter
    def enterpriseObjectId(self, enterpriseObjectId):
        """
        Sets the enterpriseObjectId of this EnterpriseGetEnterpriseAlertsResultItem.

        :param enterpriseObjectId: The enterpriseObjectId of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: int
        """

        self._enterpriseObjectId = enterpriseObjectId

    @property
    def enterpriseObjectName(self):
        """
        Gets the enterpriseObjectName of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The enterpriseObjectName of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: str
        """
        return self._enterpriseObjectName

    @enterpriseObjectName.setter
    def enterpriseObjectName(self, enterpriseObjectName):
        """
        Sets the enterpriseObjectName of this EnterpriseGetEnterpriseAlertsResultItem.

        :param enterpriseObjectName: The enterpriseObjectName of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: str
        """

        self._enterpriseObjectName = enterpriseObjectName

    @property
    def name(self):
        """
        Gets the name of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The name of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this EnterpriseGetEnterpriseAlertsResultItem.

        :param name: The name of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: str
        """

        self._name = name

    @property
    def type(self):
        """
        Gets the type of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The type of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        Sets the type of this EnterpriseGetEnterpriseAlertsResultItem.

        :param type: The type of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: str
        """

        self._type = type

    @property
    def state(self):
        """
        Gets the state of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The state of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """
        Sets the state of this EnterpriseGetEnterpriseAlertsResultItem.

        :param state: The state of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: str
        """

        self._state = state

    @property
    def stateSetTime(self):
        """
        Gets the stateSetTime of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The stateSetTime of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: datetime
        """
        return self._stateSetTime

    @stateSetTime.setter
    def stateSetTime(self, stateSetTime):
        """
        Sets the stateSetTime of this EnterpriseGetEnterpriseAlertsResultItem.

        :param stateSetTime: The stateSetTime of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: datetime
        """

        self._stateSetTime = stateSetTime

    @property
    def lastContact(self):
        """
        Gets the lastContact of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The lastContact of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: datetime
        """
        return self._lastContact

    @lastContact.setter
    def lastContact(self, lastContact):
        """
        Sets the lastContact of this EnterpriseGetEnterpriseAlertsResultItem.

        :param lastContact: The lastContact of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: datetime
        """

        self._lastContact = lastContact

    @property
    def firstNotificationSeconds(self):
        """
        Gets the firstNotificationSeconds of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The firstNotificationSeconds of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: int
        """
        return self._firstNotificationSeconds

    @firstNotificationSeconds.setter
    def firstNotificationSeconds(self, firstNotificationSeconds):
        """
        Sets the firstNotificationSeconds of this EnterpriseGetEnterpriseAlertsResultItem.

        :param firstNotificationSeconds: The firstNotificationSeconds of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: int
        """

        self._firstNotificationSeconds = firstNotificationSeconds

    @property
    def maxNotifications(self):
        """
        Gets the maxNotifications of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The maxNotifications of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: int
        """
        return self._maxNotifications

    @maxNotifications.setter
    def maxNotifications(self, maxNotifications):
        """
        Sets the maxNotifications of this EnterpriseGetEnterpriseAlertsResultItem.

        :param maxNotifications: The maxNotifications of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: int
        """

        self._maxNotifications = maxNotifications

    @property
    def notificationIntervalSeconds(self):
        """
        Gets the notificationIntervalSeconds of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The notificationIntervalSeconds of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: int
        """
        return self._notificationIntervalSeconds

    @notificationIntervalSeconds.setter
    def notificationIntervalSeconds(self, notificationIntervalSeconds):
        """
        Sets the notificationIntervalSeconds of this EnterpriseGetEnterpriseAlertsResultItem.

        :param notificationIntervalSeconds: The notificationIntervalSeconds of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: int
        """

        self._notificationIntervalSeconds = notificationIntervalSeconds

    @property
    def resetIntervalSeconds(self):
        """
        Gets the resetIntervalSeconds of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The resetIntervalSeconds of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: int
        """
        return self._resetIntervalSeconds

    @resetIntervalSeconds.setter
    def resetIntervalSeconds(self, resetIntervalSeconds):
        """
        Sets the resetIntervalSeconds of this EnterpriseGetEnterpriseAlertsResultItem.

        :param resetIntervalSeconds: The resetIntervalSeconds of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: int
        """

        self._resetIntervalSeconds = resetIntervalSeconds

    @property
    def comment(self):
        """
        Gets the comment of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The comment of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: str
        """
        return self._comment

    @comment.setter
    def comment(self, comment):
        """
        Sets the comment of this EnterpriseGetEnterpriseAlertsResultItem.

        :param comment: The comment of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: str
        """

        self._comment = comment

    @property
    def nextNotificationTime(self):
        """
        Gets the nextNotificationTime of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The nextNotificationTime of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: datetime
        """
        return self._nextNotificationTime

    @nextNotificationTime.setter
    def nextNotificationTime(self, nextNotificationTime):
        """
        Sets the nextNotificationTime of this EnterpriseGetEnterpriseAlertsResultItem.

        :param nextNotificationTime: The nextNotificationTime of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: datetime
        """

        self._nextNotificationTime = nextNotificationTime

    @property
    def remainingNotifications(self):
        """
        Gets the remainingNotifications of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The remainingNotifications of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: int
        """
        return self._remainingNotifications

    @remainingNotifications.setter
    def remainingNotifications(self, remainingNotifications):
        """
        Sets the remainingNotifications of this EnterpriseGetEnterpriseAlertsResultItem.

        :param remainingNotifications: The remainingNotifications of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: int
        """

        self._remainingNotifications = remainingNotifications

    @property
    def timezone(self):
        """
        Gets the timezone of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The timezone of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: str
        """
        return self._timezone

    @timezone.setter
    def timezone(self, timezone):
        """
        Sets the timezone of this EnterpriseGetEnterpriseAlertsResultItem.

        :param timezone: The timezone of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: str
        """

        self._timezone = timezone

    @property
    def locale(self):
        """
        Gets the locale of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The locale of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: str
        """
        return self._locale

    @locale.setter
    def locale(self, locale):
        """
        Sets the locale of this EnterpriseGetEnterpriseAlertsResultItem.

        :param locale: The locale of this EnterpriseGetEnterpriseAlertsResultItem.
        :type: str
        """

        self._locale = locale

    @property
    def modified(self):
        """
        Gets the modified of this EnterpriseGetEnterpriseAlertsResultItem.

        :return: The modified of this EnterpriseGetEnterpriseAlertsResultItem.
        :rtype: datetime
        """
        return self._modified

    @modified.setter
    def modified(self, modified):
        """
        Sets the modified of this EnterpriseGetEnterpriseAlertsResultItem.

        :param modified: The modified of this EnterpriseGetEnterpriseAlertsResultItem.
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
        if not isinstance(other, EnterpriseGetEnterpriseAlertsResultItem):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
