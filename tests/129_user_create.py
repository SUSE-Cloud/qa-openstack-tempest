#!/usr/bin/python

import sys
sys.path.append('./')

import json
from base_test import BaseTest

def test_create_user_by_name(username, password, tenant_name):
    """ test administrator to create a user whose name is the giving name"""
    bt = BaseTest()
    endpoint = bt.get_service_endpoint('keystone')
    endpoint = endpoint + '/users'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    tenant = bt.get_tenant_by_name(tenant_name)
    user = bt.get_user_by_name(username)

    if tenant == None or user != None:
        return 3

    body = {
            'user': {
                'name': username,
                'password': password,
                'tenantId': tenant['id'],
                'email': 'jyao@suse.com',
                'enabled': True
            }
        }

    response, content = bt.post(endpoint, headers=headers, body=json.dumps(body))

    if(response['status'] == '200'):
        return 0
    return 1

ret = test_create_user_by_name('test_create_user', 'crowbar', 'test_create_tenant')
exit(ret)
