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


class MonitoringGetAggregateEdgeLinkMetricsResultItem(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, bestJitterMsRx=None, bestJitterMsTx=None, bestLatencyMsRx=None, bestLatencyMsTx=None, bestLossPctRx=None, bestLossPctTx=None, bpsOfBestPathRx=None, bpsOfBestPathTx=None, bytesRx=None, bytesTx=None, controlBytesRx=None, controlBytesTx=None, controlPacketsRx=None, controlPacketsTx=None, link=None, linkId=None, name=None, p1BytesRx=None, p1BytesTx=None, p1PacketsRx=None, p1PacketsTx=None, p2BytesRx=None, p2BytesTx=None, p2PacketsRx=None, p2PacketsTx=None, p3BytesRx=None, p3BytesTx=None, p3PacketsRx=None, p3PacketsTx=None, scoreRx=None, scoreTx=None, signalStrength=None, state=None):
        """
        MonitoringGetAggregateEdgeLinkMetricsResultItem - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'bestJitterMsRx': 'int',
            'bestJitterMsTx': 'int',
            'bestLatencyMsRx': 'int',
            'bestLatencyMsTx': 'int',
            'bestLossPctRx': 'int',
            'bestLossPctTx': 'int',
            'bpsOfBestPathRx': 'int',
            'bpsOfBestPathTx': 'int',
            'bytesRx': 'int',
            'bytesTx': 'int',
            'controlBytesRx': 'int',
            'controlBytesTx': 'int',
            'controlPacketsRx': 'int',
            'controlPacketsTx': 'int',
            'link': 'MonitoringGetAggregateEdgeLinkMetricsResultItemLink',
            'linkId': 'int',
            'name': 'str',
            'p1BytesRx': 'int',
            'p1BytesTx': 'int',
            'p1PacketsRx': 'int',
            'p1PacketsTx': 'int',
            'p2BytesRx': 'int',
            'p2BytesTx': 'int',
            'p2PacketsRx': 'int',
            'p2PacketsTx': 'int',
            'p3BytesRx': 'int',
            'p3BytesTx': 'int',
            'p3PacketsRx': 'int',
            'p3PacketsTx': 'int',
            'scoreRx': 'int',
            'scoreTx': 'int',
            'signalStrength': 'int',
            'state': 'int'
        }

        self.attribute_map = {
            'bestJitterMsRx': 'bestJitterMsRx',
            'bestJitterMsTx': 'bestJitterMsTx',
            'bestLatencyMsRx': 'bestLatencyMsRx',
            'bestLatencyMsTx': 'bestLatencyMsTx',
            'bestLossPctRx': 'bestLossPctRx',
            'bestLossPctTx': 'bestLossPctTx',
            'bpsOfBestPathRx': 'bpsOfBestPathRx',
            'bpsOfBestPathTx': 'bpsOfBestPathTx',
            'bytesRx': 'bytesRx',
            'bytesTx': 'bytesTx',
            'controlBytesRx': 'controlBytesRx',
            'controlBytesTx': 'controlBytesTx',
            'controlPacketsRx': 'controlPacketsRx',
            'controlPacketsTx': 'controlPacketsTx',
            'link': 'link',
            'linkId': 'linkId',
            'name': 'name',
            'p1BytesRx': 'p1BytesRx',
            'p1BytesTx': 'p1BytesTx',
            'p1PacketsRx': 'p1PacketsRx',
            'p1PacketsTx': 'p1PacketsTx',
            'p2BytesRx': 'p2BytesRx',
            'p2BytesTx': 'p2BytesTx',
            'p2PacketsRx': 'p2PacketsRx',
            'p2PacketsTx': 'p2PacketsTx',
            'p3BytesRx': 'p3BytesRx',
            'p3BytesTx': 'p3BytesTx',
            'p3PacketsRx': 'p3PacketsRx',
            'p3PacketsTx': 'p3PacketsTx',
            'scoreRx': 'scoreRx',
            'scoreTx': 'scoreTx',
            'signalStrength': 'signalStrength',
            'state': 'state'
        }

        self._bestJitterMsRx = bestJitterMsRx
        self._bestJitterMsTx = bestJitterMsTx
        self._bestLatencyMsRx = bestLatencyMsRx
        self._bestLatencyMsTx = bestLatencyMsTx
        self._bestLossPctRx = bestLossPctRx
        self._bestLossPctTx = bestLossPctTx
        self._bpsOfBestPathRx = bpsOfBestPathRx
        self._bpsOfBestPathTx = bpsOfBestPathTx
        self._bytesRx = bytesRx
        self._bytesTx = bytesTx
        self._controlBytesRx = controlBytesRx
        self._controlBytesTx = controlBytesTx
        self._controlPacketsRx = controlPacketsRx
        self._controlPacketsTx = controlPacketsTx
        self._link = link
        self._linkId = linkId
        self._name = name
        self._p1BytesRx = p1BytesRx
        self._p1BytesTx = p1BytesTx
        self._p1PacketsRx = p1PacketsRx
        self._p1PacketsTx = p1PacketsTx
        self._p2BytesRx = p2BytesRx
        self._p2BytesTx = p2BytesTx
        self._p2PacketsRx = p2PacketsRx
        self._p2PacketsTx = p2PacketsTx
        self._p3BytesRx = p3BytesRx
        self._p3BytesTx = p3BytesTx
        self._p3PacketsRx = p3PacketsRx
        self._p3PacketsTx = p3PacketsTx
        self._scoreRx = scoreRx
        self._scoreTx = scoreTx
        self._signalStrength = signalStrength
        self._state = state

    @property
    def bestJitterMsRx(self):
        """
        Gets the bestJitterMsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The bestJitterMsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._bestJitterMsRx

    @bestJitterMsRx.setter
    def bestJitterMsRx(self, bestJitterMsRx):
        """
        Sets the bestJitterMsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param bestJitterMsRx: The bestJitterMsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._bestJitterMsRx = bestJitterMsRx

    @property
    def bestJitterMsTx(self):
        """
        Gets the bestJitterMsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The bestJitterMsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._bestJitterMsTx

    @bestJitterMsTx.setter
    def bestJitterMsTx(self, bestJitterMsTx):
        """
        Sets the bestJitterMsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param bestJitterMsTx: The bestJitterMsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._bestJitterMsTx = bestJitterMsTx

    @property
    def bestLatencyMsRx(self):
        """
        Gets the bestLatencyMsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The bestLatencyMsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._bestLatencyMsRx

    @bestLatencyMsRx.setter
    def bestLatencyMsRx(self, bestLatencyMsRx):
        """
        Sets the bestLatencyMsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param bestLatencyMsRx: The bestLatencyMsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._bestLatencyMsRx = bestLatencyMsRx

    @property
    def bestLatencyMsTx(self):
        """
        Gets the bestLatencyMsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The bestLatencyMsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._bestLatencyMsTx

    @bestLatencyMsTx.setter
    def bestLatencyMsTx(self, bestLatencyMsTx):
        """
        Sets the bestLatencyMsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param bestLatencyMsTx: The bestLatencyMsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._bestLatencyMsTx = bestLatencyMsTx

    @property
    def bestLossPctRx(self):
        """
        Gets the bestLossPctRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The bestLossPctRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._bestLossPctRx

    @bestLossPctRx.setter
    def bestLossPctRx(self, bestLossPctRx):
        """
        Sets the bestLossPctRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param bestLossPctRx: The bestLossPctRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._bestLossPctRx = bestLossPctRx

    @property
    def bestLossPctTx(self):
        """
        Gets the bestLossPctTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The bestLossPctTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._bestLossPctTx

    @bestLossPctTx.setter
    def bestLossPctTx(self, bestLossPctTx):
        """
        Sets the bestLossPctTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param bestLossPctTx: The bestLossPctTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._bestLossPctTx = bestLossPctTx

    @property
    def bpsOfBestPathRx(self):
        """
        Gets the bpsOfBestPathRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The bpsOfBestPathRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._bpsOfBestPathRx

    @bpsOfBestPathRx.setter
    def bpsOfBestPathRx(self, bpsOfBestPathRx):
        """
        Sets the bpsOfBestPathRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param bpsOfBestPathRx: The bpsOfBestPathRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._bpsOfBestPathRx = bpsOfBestPathRx

    @property
    def bpsOfBestPathTx(self):
        """
        Gets the bpsOfBestPathTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The bpsOfBestPathTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._bpsOfBestPathTx

    @bpsOfBestPathTx.setter
    def bpsOfBestPathTx(self, bpsOfBestPathTx):
        """
        Sets the bpsOfBestPathTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param bpsOfBestPathTx: The bpsOfBestPathTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._bpsOfBestPathTx = bpsOfBestPathTx

    @property
    def bytesRx(self):
        """
        Gets the bytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The bytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._bytesRx

    @bytesRx.setter
    def bytesRx(self, bytesRx):
        """
        Sets the bytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param bytesRx: The bytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._bytesRx = bytesRx

    @property
    def bytesTx(self):
        """
        Gets the bytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The bytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._bytesTx

    @bytesTx.setter
    def bytesTx(self, bytesTx):
        """
        Sets the bytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param bytesTx: The bytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._bytesTx = bytesTx

    @property
    def controlBytesRx(self):
        """
        Gets the controlBytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The controlBytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._controlBytesRx

    @controlBytesRx.setter
    def controlBytesRx(self, controlBytesRx):
        """
        Sets the controlBytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param controlBytesRx: The controlBytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._controlBytesRx = controlBytesRx

    @property
    def controlBytesTx(self):
        """
        Gets the controlBytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The controlBytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._controlBytesTx

    @controlBytesTx.setter
    def controlBytesTx(self, controlBytesTx):
        """
        Sets the controlBytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param controlBytesTx: The controlBytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._controlBytesTx = controlBytesTx

    @property
    def controlPacketsRx(self):
        """
        Gets the controlPacketsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The controlPacketsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._controlPacketsRx

    @controlPacketsRx.setter
    def controlPacketsRx(self, controlPacketsRx):
        """
        Sets the controlPacketsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param controlPacketsRx: The controlPacketsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._controlPacketsRx = controlPacketsRx

    @property
    def controlPacketsTx(self):
        """
        Gets the controlPacketsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The controlPacketsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._controlPacketsTx

    @controlPacketsTx.setter
    def controlPacketsTx(self, controlPacketsTx):
        """
        Sets the controlPacketsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param controlPacketsTx: The controlPacketsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._controlPacketsTx = controlPacketsTx

    @property
    def link(self):
        """
        Gets the link of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The link of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: MonitoringGetAggregateEdgeLinkMetricsResultItemLink
        """
        return self._link

    @link.setter
    def link(self, link):
        """
        Sets the link of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param link: The link of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: MonitoringGetAggregateEdgeLinkMetricsResultItemLink
        """

        self._link = link

    @property
    def linkId(self):
        """
        Gets the linkId of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The linkId of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._linkId

    @linkId.setter
    def linkId(self, linkId):
        """
        Sets the linkId of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param linkId: The linkId of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._linkId = linkId

    @property
    def name(self):
        """
        Gets the name of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The name of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param name: The name of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: str
        """

        self._name = name

    @property
    def p1BytesRx(self):
        """
        Gets the p1BytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The p1BytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._p1BytesRx

    @p1BytesRx.setter
    def p1BytesRx(self, p1BytesRx):
        """
        Sets the p1BytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param p1BytesRx: The p1BytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._p1BytesRx = p1BytesRx

    @property
    def p1BytesTx(self):
        """
        Gets the p1BytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The p1BytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._p1BytesTx

    @p1BytesTx.setter
    def p1BytesTx(self, p1BytesTx):
        """
        Sets the p1BytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param p1BytesTx: The p1BytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._p1BytesTx = p1BytesTx

    @property
    def p1PacketsRx(self):
        """
        Gets the p1PacketsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The p1PacketsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._p1PacketsRx

    @p1PacketsRx.setter
    def p1PacketsRx(self, p1PacketsRx):
        """
        Sets the p1PacketsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param p1PacketsRx: The p1PacketsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._p1PacketsRx = p1PacketsRx

    @property
    def p1PacketsTx(self):
        """
        Gets the p1PacketsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The p1PacketsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._p1PacketsTx

    @p1PacketsTx.setter
    def p1PacketsTx(self, p1PacketsTx):
        """
        Sets the p1PacketsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param p1PacketsTx: The p1PacketsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._p1PacketsTx = p1PacketsTx

    @property
    def p2BytesRx(self):
        """
        Gets the p2BytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The p2BytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._p2BytesRx

    @p2BytesRx.setter
    def p2BytesRx(self, p2BytesRx):
        """
        Sets the p2BytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param p2BytesRx: The p2BytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._p2BytesRx = p2BytesRx

    @property
    def p2BytesTx(self):
        """
        Gets the p2BytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The p2BytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._p2BytesTx

    @p2BytesTx.setter
    def p2BytesTx(self, p2BytesTx):
        """
        Sets the p2BytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param p2BytesTx: The p2BytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._p2BytesTx = p2BytesTx

    @property
    def p2PacketsRx(self):
        """
        Gets the p2PacketsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The p2PacketsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._p2PacketsRx

    @p2PacketsRx.setter
    def p2PacketsRx(self, p2PacketsRx):
        """
        Sets the p2PacketsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param p2PacketsRx: The p2PacketsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._p2PacketsRx = p2PacketsRx

    @property
    def p2PacketsTx(self):
        """
        Gets the p2PacketsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The p2PacketsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._p2PacketsTx

    @p2PacketsTx.setter
    def p2PacketsTx(self, p2PacketsTx):
        """
        Sets the p2PacketsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param p2PacketsTx: The p2PacketsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._p2PacketsTx = p2PacketsTx

    @property
    def p3BytesRx(self):
        """
        Gets the p3BytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The p3BytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._p3BytesRx

    @p3BytesRx.setter
    def p3BytesRx(self, p3BytesRx):
        """
        Sets the p3BytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param p3BytesRx: The p3BytesRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._p3BytesRx = p3BytesRx

    @property
    def p3BytesTx(self):
        """
        Gets the p3BytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The p3BytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._p3BytesTx

    @p3BytesTx.setter
    def p3BytesTx(self, p3BytesTx):
        """
        Sets the p3BytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param p3BytesTx: The p3BytesTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._p3BytesTx = p3BytesTx

    @property
    def p3PacketsRx(self):
        """
        Gets the p3PacketsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The p3PacketsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._p3PacketsRx

    @p3PacketsRx.setter
    def p3PacketsRx(self, p3PacketsRx):
        """
        Sets the p3PacketsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param p3PacketsRx: The p3PacketsRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._p3PacketsRx = p3PacketsRx

    @property
    def p3PacketsTx(self):
        """
        Gets the p3PacketsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The p3PacketsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._p3PacketsTx

    @p3PacketsTx.setter
    def p3PacketsTx(self, p3PacketsTx):
        """
        Sets the p3PacketsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param p3PacketsTx: The p3PacketsTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._p3PacketsTx = p3PacketsTx

    @property
    def scoreRx(self):
        """
        Gets the scoreRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The scoreRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._scoreRx

    @scoreRx.setter
    def scoreRx(self, scoreRx):
        """
        Sets the scoreRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param scoreRx: The scoreRx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._scoreRx = scoreRx

    @property
    def scoreTx(self):
        """
        Gets the scoreTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The scoreTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._scoreTx

    @scoreTx.setter
    def scoreTx(self, scoreTx):
        """
        Sets the scoreTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param scoreTx: The scoreTx of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._scoreTx = scoreTx

    @property
    def signalStrength(self):
        """
        Gets the signalStrength of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The signalStrength of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._signalStrength

    @signalStrength.setter
    def signalStrength(self, signalStrength):
        """
        Sets the signalStrength of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param signalStrength: The signalStrength of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._signalStrength = signalStrength

    @property
    def state(self):
        """
        Gets the state of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :return: The state of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :rtype: int
        """
        return self._state

    @state.setter
    def state(self, state):
        """
        Sets the state of this MonitoringGetAggregateEdgeLinkMetricsResultItem.

        :param state: The state of this MonitoringGetAggregateEdgeLinkMetricsResultItem.
        :type: int
        """

        self._state = state

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
        if not isinstance(other, MonitoringGetAggregateEdgeLinkMetricsResultItem):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
