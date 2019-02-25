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


class MetricsGetEdgeCategoryMetricsResultItem(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, bytesRx=None, bytesTx=None, flowCount=None, packetsRx=None, packetsTx=None, totalBytes=None, totalPackets=None, category=None, name=None):
        """
        MetricsGetEdgeCategoryMetricsResultItem - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'bytesRx': 'int',
            'bytesTx': 'int',
            'flowCount': 'int',
            'packetsRx': 'int',
            'packetsTx': 'int',
            'totalBytes': 'int',
            'totalPackets': 'int',
            'category': 'int',
            'name': 'int'
        }

        self.attribute_map = {
            'bytesRx': 'bytesRx',
            'bytesTx': 'bytesTx',
            'flowCount': 'flowCount',
            'packetsRx': 'packetsRx',
            'packetsTx': 'packetsTx',
            'totalBytes': 'totalBytes',
            'totalPackets': 'totalPackets',
            'category': 'category',
            'name': 'name'
        }

        self._bytesRx = bytesRx
        self._bytesTx = bytesTx
        self._flowCount = flowCount
        self._packetsRx = packetsRx
        self._packetsTx = packetsTx
        self._totalBytes = totalBytes
        self._totalPackets = totalPackets
        self._category = category
        self._name = name

    @property
    def bytesRx(self):
        """
        Gets the bytesRx of this MetricsGetEdgeCategoryMetricsResultItem.

        :return: The bytesRx of this MetricsGetEdgeCategoryMetricsResultItem.
        :rtype: int
        """
        return self._bytesRx

    @bytesRx.setter
    def bytesRx(self, bytesRx):
        """
        Sets the bytesRx of this MetricsGetEdgeCategoryMetricsResultItem.

        :param bytesRx: The bytesRx of this MetricsGetEdgeCategoryMetricsResultItem.
        :type: int
        """

        self._bytesRx = bytesRx

    @property
    def bytesTx(self):
        """
        Gets the bytesTx of this MetricsGetEdgeCategoryMetricsResultItem.

        :return: The bytesTx of this MetricsGetEdgeCategoryMetricsResultItem.
        :rtype: int
        """
        return self._bytesTx

    @bytesTx.setter
    def bytesTx(self, bytesTx):
        """
        Sets the bytesTx of this MetricsGetEdgeCategoryMetricsResultItem.

        :param bytesTx: The bytesTx of this MetricsGetEdgeCategoryMetricsResultItem.
        :type: int
        """

        self._bytesTx = bytesTx

    @property
    def flowCount(self):
        """
        Gets the flowCount of this MetricsGetEdgeCategoryMetricsResultItem.

        :return: The flowCount of this MetricsGetEdgeCategoryMetricsResultItem.
        :rtype: int
        """
        return self._flowCount

    @flowCount.setter
    def flowCount(self, flowCount):
        """
        Sets the flowCount of this MetricsGetEdgeCategoryMetricsResultItem.

        :param flowCount: The flowCount of this MetricsGetEdgeCategoryMetricsResultItem.
        :type: int
        """

        self._flowCount = flowCount

    @property
    def packetsRx(self):
        """
        Gets the packetsRx of this MetricsGetEdgeCategoryMetricsResultItem.

        :return: The packetsRx of this MetricsGetEdgeCategoryMetricsResultItem.
        :rtype: int
        """
        return self._packetsRx

    @packetsRx.setter
    def packetsRx(self, packetsRx):
        """
        Sets the packetsRx of this MetricsGetEdgeCategoryMetricsResultItem.

        :param packetsRx: The packetsRx of this MetricsGetEdgeCategoryMetricsResultItem.
        :type: int
        """

        self._packetsRx = packetsRx

    @property
    def packetsTx(self):
        """
        Gets the packetsTx of this MetricsGetEdgeCategoryMetricsResultItem.

        :return: The packetsTx of this MetricsGetEdgeCategoryMetricsResultItem.
        :rtype: int
        """
        return self._packetsTx

    @packetsTx.setter
    def packetsTx(self, packetsTx):
        """
        Sets the packetsTx of this MetricsGetEdgeCategoryMetricsResultItem.

        :param packetsTx: The packetsTx of this MetricsGetEdgeCategoryMetricsResultItem.
        :type: int
        """

        self._packetsTx = packetsTx

    @property
    def totalBytes(self):
        """
        Gets the totalBytes of this MetricsGetEdgeCategoryMetricsResultItem.

        :return: The totalBytes of this MetricsGetEdgeCategoryMetricsResultItem.
        :rtype: int
        """
        return self._totalBytes

    @totalBytes.setter
    def totalBytes(self, totalBytes):
        """
        Sets the totalBytes of this MetricsGetEdgeCategoryMetricsResultItem.

        :param totalBytes: The totalBytes of this MetricsGetEdgeCategoryMetricsResultItem.
        :type: int
        """

        self._totalBytes = totalBytes

    @property
    def totalPackets(self):
        """
        Gets the totalPackets of this MetricsGetEdgeCategoryMetricsResultItem.

        :return: The totalPackets of this MetricsGetEdgeCategoryMetricsResultItem.
        :rtype: int
        """
        return self._totalPackets

    @totalPackets.setter
    def totalPackets(self, totalPackets):
        """
        Sets the totalPackets of this MetricsGetEdgeCategoryMetricsResultItem.

        :param totalPackets: The totalPackets of this MetricsGetEdgeCategoryMetricsResultItem.
        :type: int
        """

        self._totalPackets = totalPackets

    @property
    def category(self):
        """
        Gets the category of this MetricsGetEdgeCategoryMetricsResultItem.

        :return: The category of this MetricsGetEdgeCategoryMetricsResultItem.
        :rtype: int
        """
        return self._category

    @category.setter
    def category(self, category):
        """
        Sets the category of this MetricsGetEdgeCategoryMetricsResultItem.

        :param category: The category of this MetricsGetEdgeCategoryMetricsResultItem.
        :type: int
        """

        self._category = category

    @property
    def name(self):
        """
        Gets the name of this MetricsGetEdgeCategoryMetricsResultItem.

        :return: The name of this MetricsGetEdgeCategoryMetricsResultItem.
        :rtype: int
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this MetricsGetEdgeCategoryMetricsResultItem.

        :param name: The name of this MetricsGetEdgeCategoryMetricsResultItem.
        :type: int
        """

        self._name = name

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
        if not isinstance(other, MetricsGetEdgeCategoryMetricsResultItem):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
