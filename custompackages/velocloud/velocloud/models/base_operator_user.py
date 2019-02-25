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


class BaseOperatorUser(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, id=None, created=None, operatorId=None, userType=None, username=None, domain=None, password=None, firstName=None, lastName=None, officePhone=None, mobilePhone=None, isNative=None, isActive=None, isLocked=None, email=None, lastLogin=None, modified=None):
        """
        BaseOperatorUser - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'int',
            'created': 'datetime',
            'operatorId': 'int',
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
            'modified': 'datetime'
        }

        self.attribute_map = {
            'id': 'id',
            'created': 'created',
            'operatorId': 'operatorId',
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
            'modified': 'modified'
        }

        self._id = id
        self._created = created
        self._operatorId = operatorId
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

    @property
    def id(self):
        """
        Gets the id of this BaseOperatorUser.

        :return: The id of this BaseOperatorUser.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this BaseOperatorUser.

        :param id: The id of this BaseOperatorUser.
        :type: int
        """

        self._id = id

    @property
    def created(self):
        """
        Gets the created of this BaseOperatorUser.

        :return: The created of this BaseOperatorUser.
        :rtype: datetime
        """
        return self._created

    @created.setter
    def created(self, created):
        """
        Sets the created of this BaseOperatorUser.

        :param created: The created of this BaseOperatorUser.
        :type: datetime
        """

        self._created = created

    @property
    def operatorId(self):
        """
        Gets the operatorId of this BaseOperatorUser.

        :return: The operatorId of this BaseOperatorUser.
        :rtype: int
        """
        return self._operatorId

    @operatorId.setter
    def operatorId(self, operatorId):
        """
        Sets the operatorId of this BaseOperatorUser.

        :param operatorId: The operatorId of this BaseOperatorUser.
        :type: int
        """

        self._operatorId = operatorId

    @property
    def userType(self):
        """
        Gets the userType of this BaseOperatorUser.

        :return: The userType of this BaseOperatorUser.
        :rtype: str
        """
        return self._userType

    @userType.setter
    def userType(self, userType):
        """
        Sets the userType of this BaseOperatorUser.

        :param userType: The userType of this BaseOperatorUser.
        :type: str
        """

        self._userType = userType

    @property
    def username(self):
        """
        Gets the username of this BaseOperatorUser.

        :return: The username of this BaseOperatorUser.
        :rtype: str
        """
        return self._username

    @username.setter
    def username(self, username):
        """
        Sets the username of this BaseOperatorUser.

        :param username: The username of this BaseOperatorUser.
        :type: str
        """

        self._username = username

    @property
    def domain(self):
        """
        Gets the domain of this BaseOperatorUser.

        :return: The domain of this BaseOperatorUser.
        :rtype: str
        """
        return self._domain

    @domain.setter
    def domain(self, domain):
        """
        Sets the domain of this BaseOperatorUser.

        :param domain: The domain of this BaseOperatorUser.
        :type: str
        """

        self._domain = domain

    @property
    def password(self):
        """
        Gets the password of this BaseOperatorUser.

        :return: The password of this BaseOperatorUser.
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """
        Sets the password of this BaseOperatorUser.

        :param password: The password of this BaseOperatorUser.
        :type: str
        """

        self._password = password

    @property
    def firstName(self):
        """
        Gets the firstName of this BaseOperatorUser.

        :return: The firstName of this BaseOperatorUser.
        :rtype: str
        """
        return self._firstName

    @firstName.setter
    def firstName(self, firstName):
        """
        Sets the firstName of this BaseOperatorUser.

        :param firstName: The firstName of this BaseOperatorUser.
        :type: str
        """

        self._firstName = firstName

    @property
    def lastName(self):
        """
        Gets the lastName of this BaseOperatorUser.

        :return: The lastName of this BaseOperatorUser.
        :rtype: str
        """
        return self._lastName

    @lastName.setter
    def lastName(self, lastName):
        """
        Sets the lastName of this BaseOperatorUser.

        :param lastName: The lastName of this BaseOperatorUser.
        :type: str
        """

        self._lastName = lastName

    @property
    def officePhone(self):
        """
        Gets the officePhone of this BaseOperatorUser.

        :return: The officePhone of this BaseOperatorUser.
        :rtype: str
        """
        return self._officePhone

    @officePhone.setter
    def officePhone(self, officePhone):
        """
        Sets the officePhone of this BaseOperatorUser.

        :param officePhone: The officePhone of this BaseOperatorUser.
        :type: str
        """

        self._officePhone = officePhone

    @property
    def mobilePhone(self):
        """
        Gets the mobilePhone of this BaseOperatorUser.

        :return: The mobilePhone of this BaseOperatorUser.
        :rtype: str
        """
        return self._mobilePhone

    @mobilePhone.setter
    def mobilePhone(self, mobilePhone):
        """
        Sets the mobilePhone of this BaseOperatorUser.

        :param mobilePhone: The mobilePhone of this BaseOperatorUser.
        :type: str
        """

        self._mobilePhone = mobilePhone

    @property
    def isNative(self):
        """
        Gets the isNative of this BaseOperatorUser.

        :return: The isNative of this BaseOperatorUser.
        :rtype: bool
        """
        return self._isNative

    @isNative.setter
    def isNative(self, isNative):
        """
        Sets the isNative of this BaseOperatorUser.

        :param isNative: The isNative of this BaseOperatorUser.
        :type: bool
        """

        self._isNative = isNative

    @property
    def isActive(self):
        """
        Gets the isActive of this BaseOperatorUser.

        :return: The isActive of this BaseOperatorUser.
        :rtype: bool
        """
        return self._isActive

    @isActive.setter
    def isActive(self, isActive):
        """
        Sets the isActive of this BaseOperatorUser.

        :param isActive: The isActive of this BaseOperatorUser.
        :type: bool
        """

        self._isActive = isActive

    @property
    def isLocked(self):
        """
        Gets the isLocked of this BaseOperatorUser.

        :return: The isLocked of this BaseOperatorUser.
        :rtype: bool
        """
        return self._isLocked

    @isLocked.setter
    def isLocked(self, isLocked):
        """
        Sets the isLocked of this BaseOperatorUser.

        :param isLocked: The isLocked of this BaseOperatorUser.
        :type: bool
        """

        self._isLocked = isLocked

    @property
    def email(self):
        """
        Gets the email of this BaseOperatorUser.

        :return: The email of this BaseOperatorUser.
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email):
        """
        Sets the email of this BaseOperatorUser.

        :param email: The email of this BaseOperatorUser.
        :type: str
        """

        self._email = email

    @property
    def lastLogin(self):
        """
        Gets the lastLogin of this BaseOperatorUser.

        :return: The lastLogin of this BaseOperatorUser.
        :rtype: datetime
        """
        return self._lastLogin

    @lastLogin.setter
    def lastLogin(self, lastLogin):
        """
        Sets the lastLogin of this BaseOperatorUser.

        :param lastLogin: The lastLogin of this BaseOperatorUser.
        :type: datetime
        """

        self._lastLogin = lastLogin

    @property
    def modified(self):
        """
        Gets the modified of this BaseOperatorUser.

        :return: The modified of this BaseOperatorUser.
        :rtype: datetime
        """
        return self._modified

    @modified.setter
    def modified(self, modified):
        """
        Sets the modified of this BaseOperatorUser.

        :param modified: The modified of this BaseOperatorUser.
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
        if not isinstance(other, BaseOperatorUser):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
