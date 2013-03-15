#!/usr/bin/python

import sys
sys.path.append('/home/yaojia/tempest.essex')
sys.path.append('/home/yaojia/tempest.essex/qa-openstack-tempest')

import json
from base_test import BaseTest

def test_create_tenant_by_name(name):
    """ test administrator to create a tenant whose name is the giving name """
    bt = BaseTest()
    endpoint = bt.get_service_endpoint('keystone')
    endpoint = endpoint + '/tenants'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    body = {
                "tenant": {
                    "name": name,
                    "description": "test create tenant",
                    "enabled": "true",
                },
    }
    
    response, content = bt.post(endpoint, headers=headers, body=json.dumps(body))

    if(response['status'] == '200'):
        return 0
    return 1


ret = test_create_tenant_by_name('test_create_tenant')
exit(ret)
