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


class GatewayPoolGatewayIpsecGatewayDetail(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, strictHostCheck=None, strictHostCheckDN=None):
        """
        GatewayPoolGatewayIpsecGatewayDetail - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'strictHostCheck': 'bool',
            'strictHostCheckDN': 'str'
        }

        self.attribute_map = {
            'strictHostCheck': 'strictHostCheck',
            'strictHostCheckDN': 'strictHostCheckDN'
        }

        self._strictHostCheck = strictHostCheck
        self._strictHostCheckDN = strictHostCheckDN

    @property
    def strictHostCheck(self):
        """
        Gets the strictHostCheck of this GatewayPoolGatewayIpsecGatewayDetail.

        :return: The strictHostCheck of this GatewayPoolGatewayIpsecGatewayDetail.
        :rtype: bool
        """
        return self._strictHostCheck

    @strictHostCheck.setter
    def strictHostCheck(self, strictHostCheck):
        """
        Sets the strictHostCheck of this GatewayPoolGatewayIpsecGatewayDetail.

        :param strictHostCheck: The strictHostCheck of this GatewayPoolGatewayIpsecGatewayDetail.
        :type: bool
        """

        self._strictHostCheck = strictHostCheck

    @property
    def strictHostCheckDN(self):
        """
        Gets the strictHostCheckDN of this GatewayPoolGatewayIpsecGatewayDetail.

        :return: The strictHostCheckDN of this GatewayPoolGatewayIpsecGatewayDetail.
        :rtype: str
        """
        return self._strictHostCheckDN

    @strictHostCheckDN.setter
    def strictHostCheckDN(self, strictHostCheckDN):
        """
        Sets the strictHostCheckDN of this GatewayPoolGatewayIpsecGatewayDetail.

        :param strictHostCheckDN: The strictHostCheckDN of this GatewayPoolGatewayIpsecGatewayDetail.
        :type: str
        """

        self._strictHostCheckDN = strictHostCheckDN

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
        if not isinstance(other, GatewayPoolGatewayIpsecGatewayDetail):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
