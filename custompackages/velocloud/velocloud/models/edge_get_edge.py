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


class EdgeGetEdge(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, id=None, enterpriseId=None, logicalId=None, activationKey=None, _with=None):
        """
        EdgeGetEdge - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'int',
            'enterpriseId': 'int',
            'logicalId': 'str',
            'activationKey': 'str',
            '_with': 'list[str]'
        }

        self.attribute_map = {
            'id': 'id',
            'enterpriseId': 'enterpriseId',
            'logicalId': 'logicalId',
            'activationKey': 'activationKey',
            '_with': 'with'
        }

        self._id = id
        self._enterpriseId = enterpriseId
        self._logicalId = logicalId
        self._activationKey = activationKey
        self.__with = _with

    @property
    def id(self):
        """
        Gets the id of this EdgeGetEdge.

        :return: The id of this EdgeGetEdge.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this EdgeGetEdge.

        :param id: The id of this EdgeGetEdge.
        :type: int
        """

        self._id = id

    @property
    def enterpriseId(self):
        """
        Gets the enterpriseId of this EdgeGetEdge.

        :return: The enterpriseId of this EdgeGetEdge.
        :rtype: int
        """
        return self._enterpriseId

    @enterpriseId.setter
    def enterpriseId(self, enterpriseId):
        """
        Sets the enterpriseId of this EdgeGetEdge.

        :param enterpriseId: The enterpriseId of this EdgeGetEdge.
        :type: int
        """

        self._enterpriseId = enterpriseId

    @property
    def logicalId(self):
        """
        Gets the logicalId of this EdgeGetEdge.

        :return: The logicalId of this EdgeGetEdge.
        :rtype: str
        """
        return self._logicalId

    @logicalId.setter
    def logicalId(self, logicalId):
        """
        Sets the logicalId of this EdgeGetEdge.

        :param logicalId: The logicalId of this EdgeGetEdge.
        :type: str
        """

        self._logicalId = logicalId

    @property
    def activationKey(self):
        """
        Gets the activationKey of this EdgeGetEdge.

        :return: The activationKey of this EdgeGetEdge.
        :rtype: str
        """
        return self._activationKey

    @activationKey.setter
    def activationKey(self, activationKey):
        """
        Sets the activationKey of this EdgeGetEdge.

        :param activationKey: The activationKey of this EdgeGetEdge.
        :type: str
        """

        self._activationKey = activationKey

    @property
    def _with(self):
        """
        Gets the _with of this EdgeGetEdge.

        :return: The _with of this EdgeGetEdge.
        :rtype: list[str]
        """
        return self.__with

    @_with.setter
    def _with(self, _with):
        """
        Sets the _with of this EdgeGetEdge.

        :param _with: The _with of this EdgeGetEdge.
        :type: list[str]
        """

        self.__with = _with

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
        if not isinstance(other, EdgeGetEdge):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
