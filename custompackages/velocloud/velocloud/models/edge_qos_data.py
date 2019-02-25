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


class EdgeQOSData(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, rules=None, defaults=None, webProxy=None, serviceRateLimit=None, cosMapping=None):
        """
        EdgeQOSData - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'rules': 'list[EdgeQOSDataRules]',
            'defaults': 'list[object]',
            'webProxy': 'EdgeQOSDataWebProxy',
            'serviceRateLimit': 'EdgeQOSDataServiceRateLimit',
            'cosMapping': 'EdgeQOSDataCosMapping'
        }

        self.attribute_map = {
            'rules': 'rules',
            'defaults': 'defaults',
            'webProxy': 'webProxy',
            'serviceRateLimit': 'serviceRateLimit',
            'cosMapping': 'cosMapping'
        }

        self._rules = rules
        self._defaults = defaults
        self._webProxy = webProxy
        self._serviceRateLimit = serviceRateLimit
        self._cosMapping = cosMapping

    @property
    def rules(self):
        """
        Gets the rules of this EdgeQOSData.

        :return: The rules of this EdgeQOSData.
        :rtype: list[EdgeQOSDataRules]
        """
        return self._rules

    @rules.setter
    def rules(self, rules):
        """
        Sets the rules of this EdgeQOSData.

        :param rules: The rules of this EdgeQOSData.
        :type: list[EdgeQOSDataRules]
        """

        self._rules = rules

    @property
    def defaults(self):
        """
        Gets the defaults of this EdgeQOSData.

        :return: The defaults of this EdgeQOSData.
        :rtype: list[object]
        """
        return self._defaults

    @defaults.setter
    def defaults(self, defaults):
        """
        Sets the defaults of this EdgeQOSData.

        :param defaults: The defaults of this EdgeQOSData.
        :type: list[object]
        """

        self._defaults = defaults

    @property
    def webProxy(self):
        """
        Gets the webProxy of this EdgeQOSData.

        :return: The webProxy of this EdgeQOSData.
        :rtype: EdgeQOSDataWebProxy
        """
        return self._webProxy

    @webProxy.setter
    def webProxy(self, webProxy):
        """
        Sets the webProxy of this EdgeQOSData.

        :param webProxy: The webProxy of this EdgeQOSData.
        :type: EdgeQOSDataWebProxy
        """

        self._webProxy = webProxy

    @property
    def serviceRateLimit(self):
        """
        Gets the serviceRateLimit of this EdgeQOSData.

        :return: The serviceRateLimit of this EdgeQOSData.
        :rtype: EdgeQOSDataServiceRateLimit
        """
        return self._serviceRateLimit

    @serviceRateLimit.setter
    def serviceRateLimit(self, serviceRateLimit):
        """
        Sets the serviceRateLimit of this EdgeQOSData.

        :param serviceRateLimit: The serviceRateLimit of this EdgeQOSData.
        :type: EdgeQOSDataServiceRateLimit
        """

        self._serviceRateLimit = serviceRateLimit

    @property
    def cosMapping(self):
        """
        Gets the cosMapping of this EdgeQOSData.

        :return: The cosMapping of this EdgeQOSData.
        :rtype: EdgeQOSDataCosMapping
        """
        return self._cosMapping

    @cosMapping.setter
    def cosMapping(self, cosMapping):
        """
        Sets the cosMapping of this EdgeQOSData.

        :param cosMapping: The cosMapping of this EdgeQOSData.
        :type: EdgeQOSDataCosMapping
        """

        self._cosMapping = cosMapping

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
        if not isinstance(other, EdgeQOSData):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
