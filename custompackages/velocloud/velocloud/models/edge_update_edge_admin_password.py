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


class EdgeUpdateEdgeAdminPassword(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, id=None, username=None, password=None):
        """
        EdgeUpdateEdgeAdminPassword - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'int',
            'username': 'str',
            'password': 'str'
        }

        self.attribute_map = {
            'id': 'id',
            'username': 'username',
            'password': 'password'
        }

        self._id = id
        self._username = username
        self._password = password

    @property
    def id(self):
        """
        Gets the id of this EdgeUpdateEdgeAdminPassword.

        :return: The id of this EdgeUpdateEdgeAdminPassword.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this EdgeUpdateEdgeAdminPassword.

        :param id: The id of this EdgeUpdateEdgeAdminPassword.
        :type: int
        """

        self._id = id

    @property
    def username(self):
        """
        Gets the username of this EdgeUpdateEdgeAdminPassword.

        :return: The username of this EdgeUpdateEdgeAdminPassword.
        :rtype: str
        """
        return self._username

    @username.setter
    def username(self, username):
        """
        Sets the username of this EdgeUpdateEdgeAdminPassword.

        :param username: The username of this EdgeUpdateEdgeAdminPassword.
        :type: str
        """

        self._username = username

    @property
    def password(self):
        """
        Gets the password of this EdgeUpdateEdgeAdminPassword.

        :return: The password of this EdgeUpdateEdgeAdminPassword.
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """
        Sets the password of this EdgeUpdateEdgeAdminPassword.

        :param password: The password of this EdgeUpdateEdgeAdminPassword.
        :type: str
        """

        self._password = password

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
        if not isinstance(other, EdgeUpdateEdgeAdminPassword):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
