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


class EnterpriseGetEnterpriseGatewayHandoffResult(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, enterpriseId=None, value=None, id=None, created=None, name=None, isPassword=None, dataType=None, description=None, modified=None):
        """
        EnterpriseGetEnterpriseGatewayHandoffResult - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'enterpriseId': 'int',
            'value': 'GatewayHandoffValue',
            'id': 'int',
            'created': 'datetime',
            'name': 'str',
            'isPassword': 'bool',
            'dataType': 'str',
            'description': 'str',
            'modified': 'datetime'
        }

        self.attribute_map = {
            'enterpriseId': 'enterpriseId',
            'value': 'value',
            'id': 'id',
            'created': 'created',
            'name': 'name',
            'isPassword': 'isPassword',
            'dataType': 'dataType',
            'description': 'description',
            'modified': 'modified'
        }

        self._enterpriseId = enterpriseId
        self._value = value
        self._id = id
        self._created = created
        self._name = name
        self._isPassword = isPassword
        self._dataType = dataType
        self._description = description
        self._modified = modified

    @property
    def enterpriseId(self):
        """
        Gets the enterpriseId of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :return: The enterpriseId of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :rtype: int
        """
        return self._enterpriseId

    @enterpriseId.setter
    def enterpriseId(self, enterpriseId):
        """
        Sets the enterpriseId of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :param enterpriseId: The enterpriseId of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :type: int
        """

        self._enterpriseId = enterpriseId

    @property
    def value(self):
        """
        Gets the value of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :return: The value of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :rtype: GatewayHandoffValue
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Sets the value of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :param value: The value of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :type: GatewayHandoffValue
        """

        self._value = value

    @property
    def id(self):
        """
        Gets the id of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :return: The id of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :param id: The id of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :type: int
        """

        self._id = id

    @property
    def created(self):
        """
        Gets the created of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :return: The created of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :rtype: datetime
        """
        return self._created

    @created.setter
    def created(self, created):
        """
        Sets the created of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :param created: The created of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :type: datetime
        """

        self._created = created

    @property
    def name(self):
        """
        Gets the name of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :return: The name of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :param name: The name of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :type: str
        """

        self._name = name

    @property
    def isPassword(self):
        """
        Gets the isPassword of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :return: The isPassword of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :rtype: bool
        """
        return self._isPassword

    @isPassword.setter
    def isPassword(self, isPassword):
        """
        Sets the isPassword of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :param isPassword: The isPassword of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :type: bool
        """

        self._isPassword = isPassword

    @property
    def dataType(self):
        """
        Gets the dataType of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :return: The dataType of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :rtype: str
        """
        return self._dataType

    @dataType.setter
    def dataType(self, dataType):
        """
        Sets the dataType of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :param dataType: The dataType of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :type: str
        """

        self._dataType = dataType

    @property
    def description(self):
        """
        Gets the description of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :return: The description of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :param description: The description of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :type: str
        """

        self._description = description

    @property
    def modified(self):
        """
        Gets the modified of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :return: The modified of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :rtype: datetime
        """
        return self._modified

    @modified.setter
    def modified(self, modified):
        """
        Sets the modified of this EnterpriseGetEnterpriseGatewayHandoffResult.

        :param modified: The modified of this EnterpriseGetEnterpriseGatewayHandoffResult.
        :type: datetime
        """

        self._modified = modified

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
        if not isinstance(other, EnterpriseGetEnterpriseGatewayHandoffResult):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
