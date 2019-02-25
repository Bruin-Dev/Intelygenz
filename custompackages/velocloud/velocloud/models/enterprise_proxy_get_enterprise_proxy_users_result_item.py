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


class EnterpriseProxyGetEnterpriseProxyUsersResultItem(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, id=None, created=None, userType=None, username=None, domain=None, password=None, firstName=None, lastName=None, officePhone=None, mobilePhone=None, isNative=None, isActive=None, isLocked=None, email=None, lastLogin=None, modified=None, roleId=None, roleName=None, enterpriseProxyId=None, networkId=None):
        """
        EnterpriseProxyGetEnterpriseProxyUsersResultItem - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'int',
            'created': 'datetime',
            'userType': 'str',
            'username': 'str',
            'domain': 'str',
            'password': 'str',
            'firstName': 'str',
            'lastName': 'str',
            'officePhone': 'str',
            'mobilePhone': 'str',
            'isNative': 'bool',
            'isActive': 'bool',
            'isLocked': 'bool',
            'email': 'str',
            'lastLogin': 'datetime',
            'modified': 'datetime',
            'roleId': 'int',
            'roleName': 'str',
            'enterpriseProxyId': 'int',
            'networkId': 'int'
        }

        self.attribute_map = {
            'id': 'id',
            'created': 'created',
            'userType': 'userType',
            'username': 'username',
            'domain': 'domain',
            'password': 'password',
            'firstName': 'firstName',
            'lastName': 'lastName',
            'officePhone': 'officePhone',
            'mobilePhone': 'mobilePhone',
            'isNative': 'isNative',
            'isActive': 'isActive',
            'isLocked': 'isLocked',
            'email': 'email',
            'lastLogin': 'lastLogin',
            'modified': 'modified',
            'roleId': 'roleId',
            'roleName': 'roleName',
            'enterpriseProxyId': 'enterpriseProxyId',
            'networkId': 'networkId'
        }

        self._id = id
        self._created = created
        self._userType = userType
        self._username = username
        self._domain = domain
        self._password = password
        self._firstName = firstName
        self._lastName = lastName
        self._officePhone = officePhone
        self._mobilePhone = mobilePhone
        self._isNative = isNative
        self._isActive = isActive
        self._isLocked = isLocked
        self._email = email
        self._lastLogin = lastLogin
        self._modified = modified
        self._roleId = roleId
        self._roleName = roleName
        self._enterpriseProxyId = enterpriseProxyId
        self._networkId = networkId

    @property
    def id(self):
        """
        Gets the id of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The id of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param id: The id of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: int
        """

        self._id = id

    @property
    def created(self):
        """
        Gets the created of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The created of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: datetime
        """
        return self._created

    @created.setter
    def created(self, created):
        """
        Sets the created of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param created: The created of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: datetime
        """

        self._created = created

    @property
    def userType(self):
        """
        Gets the userType of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The userType of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: str
        """
        return self._userType

    @userType.setter
    def userType(self, userType):
        """
        Sets the userType of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param userType: The userType of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: str
        """

        self._userType = userType

    @property
    def username(self):
        """
        Gets the username of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The username of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: str
        """
        return self._username

    @username.setter
    def username(self, username):
        """
        Sets the username of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param username: The username of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: str
        """

        self._username = username

    @property
    def domain(self):
        """
        Gets the domain of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The domain of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: str
        """
        return self._domain

    @domain.setter
    def domain(self, domain):
        """
        Sets the domain of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param domain: The domain of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: str
        """

        self._domain = domain

    @property
    def password(self):
        """
        Gets the password of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The password of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """
        Sets the password of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param password: The password of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: str
        """

        self._password = password

    @property
    def firstName(self):
        """
        Gets the firstName of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The firstName of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: str
        """
        return self._firstName

    @firstName.setter
    def firstName(self, firstName):
        """
        Sets the firstName of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param firstName: The firstName of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: str
        """

        self._firstName = firstName

    @property
    def lastName(self):
        """
        Gets the lastName of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The lastName of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: str
        """
        return self._lastName

    @lastName.setter
    def lastName(self, lastName):
        """
        Sets the lastName of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param lastName: The lastName of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: str
        """

        self._lastName = lastName

    @property
    def officePhone(self):
        """
        Gets the officePhone of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The officePhone of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: str
        """
        return self._officePhone

    @officePhone.setter
    def officePhone(self, officePhone):
        """
        Sets the officePhone of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param officePhone: The officePhone of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: str
        """

        self._officePhone = officePhone

    @property
    def mobilePhone(self):
        """
        Gets the mobilePhone of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The mobilePhone of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: str
        """
        return self._mobilePhone

    @mobilePhone.setter
    def mobilePhone(self, mobilePhone):
        """
        Sets the mobilePhone of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param mobilePhone: The mobilePhone of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: str
        """

        self._mobilePhone = mobilePhone

    @property
    def isNative(self):
        """
        Gets the isNative of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The isNative of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: bool
        """
        return self._isNative

    @isNative.setter
    def isNative(self, isNative):
        """
        Sets the isNative of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param isNative: The isNative of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: bool
        """

        self._isNative = isNative

    @property
    def isActive(self):
        """
        Gets the isActive of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The isActive of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: bool
        """
        return self._isActive

    @isActive.setter
    def isActive(self, isActive):
        """
        Sets the isActive of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param isActive: The isActive of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: bool
        """

        self._isActive = isActive

    @property
    def isLocked(self):
        """
        Gets the isLocked of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The isLocked of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: bool
        """
        return self._isLocked

    @isLocked.setter
    def isLocked(self, isLocked):
        """
        Sets the isLocked of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param isLocked: The isLocked of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: bool
        """

        self._isLocked = isLocked

    @property
    def email(self):
        """
        Gets the email of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The email of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email):
        """
        Sets the email of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param email: The email of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: str
        """

        self._email = email

    @property
    def lastLogin(self):
        """
        Gets the lastLogin of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The lastLogin of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: datetime
        """
        return self._lastLogin

    @lastLogin.setter
    def lastLogin(self, lastLogin):
        """
        Sets the lastLogin of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param lastLogin: The lastLogin of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: datetime
        """

        self._lastLogin = lastLogin

    @property
    def modified(self):
        """
        Gets the modified of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The modified of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: datetime
        """
        return self._modified

    @modified.setter
    def modified(self, modified):
        """
        Sets the modified of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param modified: The modified of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: datetime
        """

        self._modified = modified

    @property
    def roleId(self):
        """
        Gets the roleId of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The roleId of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: int
        """
        return self._roleId

    @roleId.setter
    def roleId(self, roleId):
        """
        Sets the roleId of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param roleId: The roleId of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: int
        """

        self._roleId = roleId

    @property
    def roleName(self):
        """
        Gets the roleName of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The roleName of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: str
        """
        return self._roleName

    @roleName.setter
    def roleName(self, roleName):
        """
        Sets the roleName of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param roleName: The roleName of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: str
        """

        self._roleName = roleName

    @property
    def enterpriseProxyId(self):
        """
        Gets the enterpriseProxyId of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The enterpriseProxyId of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: int
        """
        return self._enterpriseProxyId

    @enterpriseProxyId.setter
    def enterpriseProxyId(self, enterpriseProxyId):
        """
        Sets the enterpriseProxyId of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param enterpriseProxyId: The enterpriseProxyId of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: int
        """

        self._enterpriseProxyId = enterpriseProxyId

    @property
    def networkId(self):
        """
        Gets the networkId of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :return: The networkId of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :rtype: int
        """
        return self._networkId

    @networkId.setter
    def networkId(self, networkId):
        """
        Sets the networkId of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.

        :param networkId: The networkId of this EnterpriseProxyGetEnterpriseProxyUsersResultItem.
        :type: int
        """

        self._networkId = networkId

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
        if not isinstance(other, EnterpriseProxyGetEnterpriseProxyUsersResultItem):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
