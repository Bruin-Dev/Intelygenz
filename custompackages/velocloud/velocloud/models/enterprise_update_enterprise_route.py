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


class EnterpriseUpdateEnterpriseRoute(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, enterpriseId=None, original=None, updated=None):
        """
        EnterpriseUpdateEnterpriseRoute - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'enterpriseId': 'int',
            'original': 'EnterpriseRouteCollection',
            'updated': 'EnterpriseRouteCollection'
        }

        self.attribute_map = {
            'enterpriseId': 'enterpriseId',
            'original': 'original',
            'updated': 'updated'
        }

        self._enterpriseId = enterpriseId
        self._original = original
        self._updated = updated

    @property
    def enterpriseId(self):
        """
        Gets the enterpriseId of this EnterpriseUpdateEnterpriseRoute.

        :return: The enterpriseId of this EnterpriseUpdateEnterpriseRoute.
        :rtype: int
        """
        return self._enterpriseId

    @enterpriseId.setter
    def enterpriseId(self, enterpriseId):
        """
        Sets the enterpriseId of this EnterpriseUpdateEnterpriseRoute.

        :param enterpriseId: The enterpriseId of this EnterpriseUpdateEnterpriseRoute.
        :type: int
        """

        self._enterpriseId = enterpriseId

    @property
    def original(self):
        """
        Gets the original of this EnterpriseUpdateEnterpriseRoute.

        :return: The original of this EnterpriseUpdateEnterpriseRoute.
        :rtype: EnterpriseRouteCollection
        """
        return self._original

    @original.setter
    def original(self, original):
        """
        Sets the original of this EnterpriseUpdateEnterpriseRoute.

        :param original: The original of this EnterpriseUpdateEnterpriseRoute.
        :type: EnterpriseRouteCollection
        """

        self._original = original

    @property
    def updated(self):
        """
        Gets the updated of this EnterpriseUpdateEnterpriseRoute.

        :return: The updated of this EnterpriseUpdateEnterpriseRoute.
        :rtype: EnterpriseRouteCollection
        """
        return self._updated

    @updated.setter
    def updated(self, updated):
        """
        Sets the updated of this EnterpriseUpdateEnterpriseRoute.

        :param updated: The updated of this EnterpriseUpdateEnterpriseRoute.
        :type: EnterpriseRouteCollection
        """

        self._updated = updated

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
        if not isinstance(other, EnterpriseUpdateEnterpriseRoute):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
