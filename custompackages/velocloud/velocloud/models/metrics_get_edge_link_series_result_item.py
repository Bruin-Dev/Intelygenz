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


class MetricsGetEdgeLinkSeriesResultItem(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, series=None, edgeId=None, link=None, linkId=None):
        """
        MetricsGetEdgeLinkSeriesResultItem - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'series': 'list[FlowMetricTimeSeriesItem]',
            'edgeId': 'int',
            'link': 'Link',
            'linkId': 'int'
        }

        self.attribute_map = {
            'series': 'series',
            'edgeId': 'edgeId',
            'link': 'link',
            'linkId': 'linkId'
        }

        self._series = series
        self._edgeId = edgeId
        self._link = link
        self._linkId = linkId

    @property
    def series(self):
        """
        Gets the series of this MetricsGetEdgeLinkSeriesResultItem.

        :return: The series of this MetricsGetEdgeLinkSeriesResultItem.
        :rtype: list[FlowMetricTimeSeriesItem]
        """
        return self._series

    @series.setter
    def series(self, series):
        """
        Sets the series of this MetricsGetEdgeLinkSeriesResultItem.

        :param series: The series of this MetricsGetEdgeLinkSeriesResultItem.
        :type: list[FlowMetricTimeSeriesItem]
        """

        self._series = series

    @property
    def edgeId(self):
        """
        Gets the edgeId of this MetricsGetEdgeLinkSeriesResultItem.

        :return: The edgeId of this MetricsGetEdgeLinkSeriesResultItem.
        :rtype: int
        """
        return self._edgeId

    @edgeId.setter
    def edgeId(self, edgeId):
        """
        Sets the edgeId of this MetricsGetEdgeLinkSeriesResultItem.

        :param edgeId: The edgeId of this MetricsGetEdgeLinkSeriesResultItem.
        :type: int
        """

        self._edgeId = edgeId

    @property
    def link(self):
        """
        Gets the link of this MetricsGetEdgeLinkSeriesResultItem.

        :return: The link of this MetricsGetEdgeLinkSeriesResultItem.
        :rtype: Link
        """
        return self._link

    @link.setter
    def link(self, link):
        """
        Sets the link of this MetricsGetEdgeLinkSeriesResultItem.

        :param link: The link of this MetricsGetEdgeLinkSeriesResultItem.
        :type: Link
        """

        self._link = link

    @property
    def linkId(self):
        """
        Gets the linkId of this MetricsGetEdgeLinkSeriesResultItem.

        :return: The linkId of this MetricsGetEdgeLinkSeriesResultItem.
        :rtype: int
        """
        return self._linkId

    @linkId.setter
    def linkId(self, linkId):
        """
        Sets the linkId of this MetricsGetEdgeLinkSeriesResultItem.

        :param linkId: The linkId of this MetricsGetEdgeLinkSeriesResultItem.
        :type: int
        """

        self._linkId = linkId

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
        if not isinstance(other, MetricsGetEdgeLinkSeriesResultItem):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
