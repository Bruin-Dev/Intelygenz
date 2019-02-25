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


class EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGateway(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, bgp=None, assigned=None):
        """
        EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGateway - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'bgp': 'EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGatewayBgp',
            'assigned': 'EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGatewayAssigned'
        }

        self.attribute_map = {
            'bgp': 'bgp',
            'assigned': 'assigned'
        }

        self._bgp = bgp
        self._assigned = assigned

    @property
    def bgp(self):
        """
        Gets the bgp of this EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGateway.

        :return: The bgp of this EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGateway.
        :rtype: EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGatewayBgp
        """
        return self._bgp

    @bgp.setter
    def bgp(self, bgp):
        """
        Sets the bgp of this EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGateway.

        :param bgp: The bgp of this EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGateway.
        :type: EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGatewayBgp
        """

        self._bgp = bgp

    @property
    def assigned(self):
        """
        Gets the assigned of this EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGateway.

        :return: The assigned of this EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGateway.
        :rtype: EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGatewayAssigned
        """
        return self._assigned

    @assigned.setter
    def assigned(self, assigned):
        """
        Sets the assigned of this EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGateway.

        :param assigned: The assigned of this EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGateway.
        :type: EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGatewayAssigned
        """

        self._assigned = assigned

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
        if not isinstance(other, EnterpriseupdateEnterpriseRouteConfigurationDataPartnerGateway):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
