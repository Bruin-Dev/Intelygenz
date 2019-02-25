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


class EnterpriseUserWithRoleInfo(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, id=None, created=None, userType=None, username=None, domain=None, password=None, firstName=None, lastName=None, officePhone=None, mobilePhone=None, isNative=None, isActive=None, isLocked=None, email=None, lastLogin=None, modified=None, roleId=None, roleName=None):
        """
        EnterpriseUserWithRoleInfo - a model defined in Swagger

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
            'roleName': 'str'
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
            'roleName': 'roleName'
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

    @property
    def id(self):
        """
        Gets the id of this EnterpriseUserWithRoleInfo.

        :return: The id of this EnterpriseUserWithRoleInfo.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this EnterpriseUserWithRoleInfo.

        :param id: The id of this EnterpriseUserWithRoleInfo.
        :type: int
        """

        self._id = id

    @property
    def created(self):
        """
        Gets the created of this EnterpriseUserWithRoleInfo.

        :return: The created of this EnterpriseUserWithRoleInfo.
        :rtype: datetime
        """
        return self._created

    @created.setter
    def created(self, created):
        """
        Sets the created of this EnterpriseUserWithRoleInfo.

        :param created: The created of this EnterpriseUserWithRoleInfo.
        :type: datetime
        """

        self._created = created

    @property
    def userType(self):
        """
        Gets the userType of this EnterpriseUserWithRoleInfo.

        :return: The userType of this EnterpriseUserWithRoleInfo.
        :rtype: str
        """
        return self._userType

    @userType.setter
    def userType(self, userType):
        """
        Sets the userType of this EnterpriseUserWithRoleInfo.

        :param userType: The userType of this EnterpriseUserWithRoleInfo.
        :type: str
        """

        self._userType = userType

    @property
    def username(self):
        """
        Gets the username of this EnterpriseUserWithRoleInfo.

        :return: The username of this EnterpriseUserWithRoleInfo.
        :rtype: str
        """
        return self._username

    @username.setter
    def username(self, username):
        """
        Sets the username of this EnterpriseUserWithRoleInfo.

        :param username: The username of this EnterpriseUserWithRoleInfo.
        :type: str
        """

        self._username = username

    @property
    def domain(self):
        """
        Gets the domain of this EnterpriseUserWithRoleInfo.

        :return: The domain of this EnterpriseUserWithRoleInfo.
        :rtype: str
        """
        return self._domain

    @domain.setter
    def domain(self, domain):
        """
        Sets the domain of this EnterpriseUserWithRoleInfo.

        :param domain: The domain of this EnterpriseUserWithRoleInfo.
        :type: str
        """

        self._domain = domain

    @property
    def password(self):
        """
        Gets the password of this EnterpriseUserWithRoleInfo.

        :return: The password of this EnterpriseUserWithRoleInfo.
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """
        Sets the password of this EnterpriseUserWithRoleInfo.

        :param password: The password of this EnterpriseUserWithRoleInfo.
        :type: str
        """

        self._password = password

    @property
    def firstName(self):
        """
        Gets the firstName of this EnterpriseUserWithRoleInfo.

        :return: The firstName of this EnterpriseUserWithRoleInfo.
        :rtype: str
        """
        return self._firstName

    @firstName.setter
    def firstName(self, firstName):
        """
        Sets the firstName of this EnterpriseUserWithRoleInfo.

        :param firstName: The firstName of this EnterpriseUserWithRoleInfo.
        :type: str
        """

        self._firstName = firstName

    @property
    def lastName(self):
        """
        Gets the lastName of this EnterpriseUserWithRoleInfo.

        :return: The lastName of this EnterpriseUserWithRoleInfo.
        :rtype: str
        """
        return self._lastName

    @lastName.setter
    def lastName(self, lastName):
        """
        Sets the lastName of this EnterpriseUserWithRoleInfo.

        :param lastName: The lastName of this EnterpriseUserWithRoleInfo.
        :type: str
        """

        self._lastName = lastName

    @property
    def officePhone(self):
        """
        Gets the officePhone of this EnterpriseUserWithRoleInfo.

        :return: The officePhone of this EnterpriseUserWithRoleInfo.
        :rtype: str
        """
        return self._officePhone

    @officePhone.setter
    def officePhone(self, officePhone):
        """
        Sets the officePhone of this EnterpriseUserWithRoleInfo.

        :param officePhone: The officePhone of this EnterpriseUserWithRoleInfo.
        :type: str
        """

        self._officePhone = officePhone

    @property
    def mobilePhone(self):
        """
        Gets the mobilePhone of this EnterpriseUserWithRoleInfo.

        :return: The mobilePhone of this EnterpriseUserWithRoleInfo.
        :rtype: str
        """
        return self._mobilePhone

    @mobilePhone.setter
    def mobilePhone(self, mobilePhone):
        """
        Sets the mobilePhone of this EnterpriseUserWithRoleInfo.

        :param mobilePhone: The mobilePhone of this EnterpriseUserWithRoleInfo.
        :type: str
        """

        self._mobilePhone = mobilePhone

    @property
    def isNative(self):
        """
        Gets the isNative of this EnterpriseUserWithRoleInfo.

        :return: The isNative of this EnterpriseUserWithRoleInfo.
        :rtype: bool
        """
        return self._isNative

    @isNative.setter
    def isNative(self, isNative):
        """
        Sets the isNative of this EnterpriseUserWithRoleInfo.

        :param isNative: The isNative of this EnterpriseUserWithRoleInfo.
        :type: bool
        """

        self._isNative = isNative

    @property
    def isActive(self):
        """
        Gets the isActive of this EnterpriseUserWithRoleInfo.

        :return: The isActive of this EnterpriseUserWithRoleInfo.
        :rtype: bool
        """
        return self._isActive

    @isActive.setter
    def isActive(self, isActive):
        """
        Sets the isActive of this EnterpriseUserWithRoleInfo.

        :param isActive: The isActive of this EnterpriseUserWithRoleInfo.
        :type: bool
        """

        self._isActive = isActive

    @property
    def isLocked(self):
        """
        Gets the isLocked of this EnterpriseUserWithRoleInfo.

        :return: The isLocked of this EnterpriseUserWithRoleInfo.
        :rtype: bool
        """
        return self._isLocked

    @isLocked.setter
    def isLocked(self, isLocked):
        """
        Sets the isLocked of this EnterpriseUserWithRoleInfo.

        :param isLocked: The isLocked of this EnterpriseUserWithRoleInfo.
        :type: bool
        """

        self._isLocked = isLocked

    @property
    def email(self):
        """
        Gets the email of this EnterpriseUserWithRoleInfo.

        :return: The email of this EnterpriseUserWithRoleInfo.
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email):
        """
        Sets the email of this EnterpriseUserWithRoleInfo.

        :param email: The email of this EnterpriseUserWithRoleInfo.
        :type: str
        """

        self._email = email

    @property
    def lastLogin(self):
        """
        Gets the lastLogin of this EnterpriseUserWithRoleInfo.

        :return: The lastLogin of this EnterpriseUserWithRoleInfo.
        :rtype: datetime
        """
        return self._lastLogin

    @lastLogin.setter
    def lastLogin(self, lastLogin):
        """
        Sets the lastLogin of this EnterpriseUserWithRoleInfo.

        :param lastLogin: The lastLogin of this EnterpriseUserWithRoleInfo.
        :type: datetime
        """

        self._lastLogin = lastLogin

    @property
    def modified(self):
        """
        Gets the modified of this EnterpriseUserWithRoleInfo.

        :return: The modified of this EnterpriseUserWithRoleInfo.
        :rtype: datetime
        """
        return self._modified

    @modified.setter
    def modified(self, modified):
        """
        Sets the modified of this EnterpriseUserWithRoleInfo.

        :param modified: The modified of this EnterpriseUserWithRoleInfo.
        :type: datetime
        """

        self._modified = modified

    @property
    def roleId(self):
        """
        Gets the roleId of this EnterpriseUserWithRoleInfo.

        :return: The roleId of this EnterpriseUserWithRoleInfo.
        :rtype: int
        """
        return self._roleId

    @roleId.setter
    def roleId(self, roleId):
        """
        Sets the roleId of this EnterpriseUserWithRoleInfo.

        :param roleId: The roleId of this EnterpriseUserWithRoleInfo.
        :type: int
        """

        self._roleId = roleId

    @property
    def roleName(self):
        """
        Gets the roleName of this EnterpriseUserWithRoleInfo.

        :return: The roleName of this EnterpriseUserWithRoleInfo.
        :rtype: str
        """
        return self._roleName

    @roleName.setter
    def roleName(self, roleName):
        """
        Sets the roleName of this EnterpriseUserWithRoleInfo.

        :param roleName: The roleName of this EnterpriseUserWithRoleInfo.
        :type: str
        """

        self._roleName = roleName

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
        if not isinstance(other, EnterpriseUserWithRoleInfo):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
