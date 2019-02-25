# coding: utf-8

"""
    Velocloud API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: 3.2.19
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import sys
import os
import re

# python 2 and python 3 compatibility library
from six import iteritems

from ..configuration import Configuration
from ..api_client import ApiClient


class NetworkApi(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        config = Configuration()
        if api_client:
            self.api_client = api_client
        else:
            if not config.api_client:
                config.api_client = ApiClient()
            self.api_client = config.api_client

    def networkDeleteNetworkGatewayPool(self, body, **kwargs):
        """
        Delete gateway pool
        Deletes the specified gateway pool (by `id`).  Privileges required:  `DELETE` `GATEWAY`
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.networkDeleteNetworkGatewayPool(body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param NetworkDeleteNetworkGatewayPool body: (required)
        :return: NetworkDeleteNetworkGatewayPoolResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.networkDeleteNetworkGatewayPool_with_http_info(body, **kwargs)
        else:
            (data) = self.networkDeleteNetworkGatewayPool_with_http_info(body, **kwargs)
            return data

    def networkDeleteNetworkGatewayPool_with_http_info(self, body, **kwargs):
        """
        Delete gateway pool
        Deletes the specified gateway pool (by `id`).  Privileges required:  `DELETE` `GATEWAY`
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.networkDeleteNetworkGatewayPool_with_http_info(body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param NetworkDeleteNetworkGatewayPool body: (required)
        :return: NetworkDeleteNetworkGatewayPoolResult
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method networkDeleteNetworkGatewayPool" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params) or (params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `networkDeleteNetworkGatewayPool`")


        collection_formats = {}

        resource_path = '/network/deleteNetworkGatewayPool'.replace('{format}', 'json')
        path_params = {}

        query_params = {}

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # Authentication setting
        auth_settings = []

        return self.api_client.call_api(resource_path, 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='NetworkDeleteNetworkGatewayPoolResult',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def networkGetNetworkConfigurations(self, body, **kwargs):
        """
        Get operator configuration profiles
        Gets all operator configuration profiles associated with an operator's network. Optionally includes the modules associated with each profile. This call does not return templates.  Privileges required:  `READ` `OPERATOR_PROFILE`
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.networkGetNetworkConfigurations(body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param NetworkGetNetworkConfigurations body: (required)
        :return: list[NetworkGetNetworkConfigurationsResultItem]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.networkGetNetworkConfigurations_with_http_info(body, **kwargs)
        else:
            (data) = self.networkGetNetworkConfigurations_with_http_info(body, **kwargs)
            return data

    def networkGetNetworkConfigurations_with_http_info(self, body, **kwargs):
        """
        Get operator configuration profiles
        Gets all operator configuration profiles associated with an operator's network. Optionally includes the modules associated with each profile. This call does not return templates.  Privileges required:  `READ` `OPERATOR_PROFILE`
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.networkGetNetworkConfigurations_with_http_info(body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param NetworkGetNetworkConfigurations body: (required)
        :return: list[NetworkGetNetworkConfigurationsResultItem]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method networkGetNetworkConfigurations" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params) or (params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `networkGetNetworkConfigurations`")


        collection_formats = {}

        resource_path = '/network/getNetworkConfigurations'.replace('{format}', 'json')
        path_params = {}

        query_params = {}

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # Authentication setting
        auth_settings = []

        return self.api_client.call_api(resource_path, 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='list[NetworkGetNetworkConfigurationsResultItem]',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def networkGetNetworkEnterprises(self, body, **kwargs):
        """
        Get a list of the enterprises on a network
        Get the enterprises existing on a network, optionally including all edges or edge counts. The `edgeConfigUpdate` \"with\" option may also be passed to check whether application of configuration updates to edges is enabled for each enterprise.  Privileges required:  `READ` `ENTERPRISE`
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.networkGetNetworkEnterprises(body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param NetworkGetNetworkEnterprises body: (required)
        :return: list[NetworkGetNetworkEnterprisesResultItem]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.networkGetNetworkEnterprises_with_http_info(body, **kwargs)
        else:
            (data) = self.networkGetNetworkEnterprises_with_http_info(body, **kwargs)
            return data

    def networkGetNetworkEnterprises_with_http_info(self, body, **kwargs):
        """
        Get a list of the enterprises on a network
        Get the enterprises existing on a network, optionally including all edges or edge counts. The `edgeConfigUpdate` \"with\" option may also be passed to check whether application of configuration updates to edges is enabled for each enterprise.  Privileges required:  `READ` `ENTERPRISE`
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.networkGetNetworkEnterprises_with_http_info(body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param NetworkGetNetworkEnterprises body: (required)
        :return: list[NetworkGetNetworkEnterprisesResultItem]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method networkGetNetworkEnterprises" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params) or (params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `networkGetNetworkEnterprises`")


        collection_formats = {}

        resource_path = '/network/getNetworkEnterprises'.replace('{format}', 'json')
        path_params = {}

        query_params = {}

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # Authentication setting
        auth_settings = []

        return self.api_client.call_api(resource_path, 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='list[NetworkGetNetworkEnterprisesResultItem]',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def networkGetNetworkGatewayPools(self, body, **kwargs):
        """
        Get list of gateway pools
        Get list of gateway pools associated with a network, optionally with the gateways or enterprises belonging to each pool.  Privileges required:  `READ` `GATEWAY`
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.networkGetNetworkGatewayPools(body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param NetworkGetNetworkGatewayPools body: (required)
        :return: list[NetworkGetNetworkGatewayPoolsResultItem]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.networkGetNetworkGatewayPools_with_http_info(body, **kwargs)
        else:
            (data) = self.networkGetNetworkGatewayPools_with_http_info(body, **kwargs)
            return data

    def networkGetNetworkGatewayPools_with_http_info(self, body, **kwargs):
        """
        Get list of gateway pools
        Get list of gateway pools associated with a network, optionally with the gateways or enterprises belonging to each pool.  Privileges required:  `READ` `GATEWAY`
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.networkGetNetworkGatewayPools_with_http_info(body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param NetworkGetNetworkGatewayPools body: (required)
        :return: list[NetworkGetNetworkGatewayPoolsResultItem]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method networkGetNetworkGatewayPools" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params) or (params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `networkGetNetworkGatewayPools`")


        collection_formats = {}

        resource_path = '/network/getNetworkGatewayPools'.replace('{format}', 'json')
        path_params = {}

        query_params = {}

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # Authentication setting
        auth_settings = []

        return self.api_client.call_api(resource_path, 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='list[NetworkGetNetworkGatewayPoolsResultItem]',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def networkGetNetworkGateways(self, body, **kwargs):
        """
        Get list of gateways
        Get list of gateways associated with a network.  Privileges required:  `READ` `GATEWAY`
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.networkGetNetworkGateways(body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param NetworkGetNetworkGateways body: (required)
        :return: list[NetworkGetNetworkGatewaysResultItem]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.networkGetNetworkGateways_with_http_info(body, **kwargs)
        else:
            (data) = self.networkGetNetworkGateways_with_http_info(body, **kwargs)
            return data

    def networkGetNetworkGateways_with_http_info(self, body, **kwargs):
        """
        Get list of gateways
        Get list of gateways associated with a network.  Privileges required:  `READ` `GATEWAY`
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.networkGetNetworkGateways_with_http_info(body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param NetworkGetNetworkGateways body: (required)
        :return: list[NetworkGetNetworkGatewaysResultItem]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method networkGetNetworkGateways" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params) or (params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `networkGetNetworkGateways`")


        collection_formats = {}

        resource_path = '/network/getNetworkGateways'.replace('{format}', 'json')
        path_params = {}

        query_params = {}

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # Authentication setting
        auth_settings = []

        return self.api_client.call_api(resource_path, 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='list[NetworkGetNetworkGatewaysResultItem]',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def networkGetNetworkOperatorUsers(self, body, **kwargs):
        """
        Get list of operator users for a network
        Get a list of all of the operator users associated with a network  Privileges required:  `READ` `OPERATOR_USER`
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.networkGetNetworkOperatorUsers(body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param NetworkGetNetworkOperatorUsers body: (required)
        :return: list[NetworkGetNetworkOperatorUsersResultItem]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.networkGetNetworkOperatorUsers_with_http_info(body, **kwargs)
        else:
            (data) = self.networkGetNetworkOperatorUsers_with_http_info(body, **kwargs)
            return data

    def networkGetNetworkOperatorUsers_with_http_info(self, body, **kwargs):
        """
        Get list of operator users for a network
        Get a list of all of the operator users associated with a network  Privileges required:  `READ` `OPERATOR_USER`
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.networkGetNetworkOperatorUsers_with_http_info(body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param NetworkGetNetworkOperatorUsers body: (required)
        :return: list[NetworkGetNetworkOperatorUsersResultItem]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method networkGetNetworkOperatorUsers" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params) or (params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `networkGetNetworkOperatorUsers`")


        collection_formats = {}

        resource_path = '/network/getNetworkOperatorUsers'.replace('{format}', 'json')
        path_params = {}

        query_params = {}

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # Authentication setting
        auth_settings = []

        return self.api_client.call_api(resource_path, 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='list[NetworkGetNetworkOperatorUsersResultItem]',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def networkInsertNetworkGatewayPool(self, body, **kwargs):
        """
        Insert a gateway pool
        Insert a gateway pool, associated with a network.  Privileges required:  `CREATE` `GATEWAY`
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.networkInsertNetworkGatewayPool(body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param NetworkInsertNetworkGatewayPool body: (required)
        :return: NetworkInsertNetworkGatewayPoolResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.networkInsertNetworkGatewayPool_with_http_info(body, **kwargs)
        else:
            (data) = self.networkInsertNetworkGatewayPool_with_http_info(body, **kwargs)
            return data

    def networkInsertNetworkGatewayPool_with_http_info(self, body, **kwargs):
        """
        Insert a gateway pool
        Insert a gateway pool, associated with a network.  Privileges required:  `CREATE` `GATEWAY`
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.networkInsertNetworkGatewayPool_with_http_info(body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param NetworkInsertNetworkGatewayPool body: (required)
        :return: NetworkInsertNetworkGatewayPoolResult
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method networkInsertNetworkGatewayPool" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params) or (params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `networkInsertNetworkGatewayPool`")


        collection_formats = {}

        resource_path = '/network/insertNetworkGatewayPool'.replace('{format}', 'json')
        path_params = {}

        query_params = {}

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # Authentication setting
        auth_settings = []

        return self.api_client.call_api(resource_path, 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='NetworkInsertNetworkGatewayPoolResult',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def networkUpdateNetworkGatewayPoolAttributes(self, body, **kwargs):
        """
        Update gateway pool attributes
        Update the configurable attributes of a Gateway Pool. Configurarable attributes are `name`, `description`, and `handOffType`.  Privileges required:  `UPDATE` `GATEWAY`
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.networkUpdateNetworkGatewayPoolAttributes(body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param NetworkUpdateNetworkGatewayPoolAttributes body: (required)
        :return: NetworkUpdateNetworkGatewayPoolAttributesResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.networkUpdateNetworkGatewayPoolAttributes_with_http_info(body, **kwargs)
        else:
            (data) = self.networkUpdateNetworkGatewayPoolAttributes_with_http_info(body, **kwargs)
            return data

    def networkUpdateNetworkGatewayPoolAttributes_with_http_info(self, body, **kwargs):
        """
        Update gateway pool attributes
        Update the configurable attributes of a Gateway Pool. Configurarable attributes are `name`, `description`, and `handOffType`.  Privileges required:  `UPDATE` `GATEWAY`
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.networkUpdateNetworkGatewayPoolAttributes_with_http_info(body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param NetworkUpdateNetworkGatewayPoolAttributes body: (required)
        :return: NetworkUpdateNetworkGatewayPoolAttributesResult
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method networkUpdateNetworkGatewayPoolAttributes" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params) or (params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `networkUpdateNetworkGatewayPoolAttributes`")


        collection_formats = {}

        resource_path = '/network/updateNetworkGatwayPoolAttributes'.replace('{format}', 'json')
        path_params = {}

        query_params = {}

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # Authentication setting
        auth_settings = []

        return self.api_client.call_api(resource_path, 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='NetworkUpdateNetworkGatewayPoolAttributesResult',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)
