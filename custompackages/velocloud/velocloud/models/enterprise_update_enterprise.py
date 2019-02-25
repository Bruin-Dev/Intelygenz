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


class EnterpriseUpdateEnterprise(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, enterpriseId=None, name=None, update=None):
        """
        EnterpriseUpdateEnterprise - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'enterpriseId': 'int',
            'name': 'str',
            'update': 'EnterpriseObject'
        }

        self.attribute_map = {
            'enterpriseId': 'enterpriseId',
            'name': 'name',
            'update': '_update'
        }

        self._enterpriseId = enterpriseId
        self._name = name
        self._update = update

    @property
    def enterpriseId(self):
        """
        Gets the enterpriseId of this EnterpriseUpdateEnterprise.

        :return: The enterpriseId of this EnterpriseUpdateEnterprise.
        :rtype: int
        """
        return self._enterpriseId

    @enterpriseId.setter
    def enterpriseId(self, enterpriseId):
        """
        Sets the enterpriseId of this EnterpriseUpdateEnterprise.

        :param enterpriseId: The enterpriseId of this EnterpriseUpdateEnterprise.
        :type: int
        """

        self._enterpriseId = enterpriseId

    @property
    def name(self):
        """
        Gets the name of this EnterpriseUpdateEnterprise.

        :return: The name of this EnterpriseUpdateEnterprise.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this EnterpriseUpdateEnterprise.

        :param name: The name of this EnterpriseUpdateEnterprise.
        :type: str
        """

        self._name = name

    @property
    def update(self):
        """
        Gets the update of this EnterpriseUpdateEnterprise.

        :return: The update of this EnterpriseUpdateEnterprise.
        :rtype: EnterpriseObject
        """
        return self._update

    @update.setter
    def update(self, update):
        """
        Sets the update of this EnterpriseUpdateEnterprise.

        :param update: The update of this EnterpriseUpdateEnterprise.
        :type: EnterpriseObject
        """

        self._update = update

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
        if not isinstance(other, EnterpriseUpdateEnterprise):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
