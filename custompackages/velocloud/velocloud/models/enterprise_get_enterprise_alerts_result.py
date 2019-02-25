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


class EnterpriseGetEnterpriseAlertsResult(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, metaData=None, data=None):
        """
        EnterpriseGetEnterpriseAlertsResult - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'metaData': 'ListMetadata',
            'data': 'list[EnterpriseGetEnterpriseAlertsResultItem]'
        }

        self.attribute_map = {
            'metaData': 'metaData',
            'data': 'data'
        }

        self._metaData = metaData
        self._data = data

    @property
    def metaData(self):
        """
        Gets the metaData of this EnterpriseGetEnterpriseAlertsResult.

        :return: The metaData of this EnterpriseGetEnterpriseAlertsResult.
        :rtype: ListMetadata
        """
        return self._metaData

    @metaData.setter
    def metaData(self, metaData):
        """
        Sets the metaData of this EnterpriseGetEnterpriseAlertsResult.

        :param metaData: The metaData of this EnterpriseGetEnterpriseAlertsResult.
        :type: ListMetadata
        """

        self._metaData = metaData

    @property
    def data(self):
        """
        Gets the data of this EnterpriseGetEnterpriseAlertsResult.

        :return: The data of this EnterpriseGetEnterpriseAlertsResult.
        :rtype: list[EnterpriseGetEnterpriseAlertsResultItem]
        """
        return self._data

    @data.setter
    def data(self, data):
        """
        Sets the data of this EnterpriseGetEnterpriseAlertsResult.

        :param data: The data of this EnterpriseGetEnterpriseAlertsResult.
        :type: list[EnterpriseGetEnterpriseAlertsResultItem]
        """

        self._data = data

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
        if not isinstance(other, EnterpriseGetEnterpriseAlertsResult):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
