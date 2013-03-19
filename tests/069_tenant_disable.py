#!/usr/bin/python

import sys
sys.path.append('./')

import json
from base_test import BaseTest
         
def test_tenant_disable(tenant_name):
    """ test disable a tenant by name given """
    
    bt = BaseTest()
    tenant = bt.get_tenant_by_name(tenant_name)

    if(tenant == None):
        return 3

    tenant_id = tenant['id']

    endpoint = bt.get_service_endpoint('keystone')
    endpoint = endpoint + '/tenants/' + tenant_id

    body = {
                "tenant": {
                    "enabled": False,
                },
    }

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    response, content = bt.post(endpoint, headers=headers, body=json.dumps(body))

    if(response['status'] == '200'):
        return 0
    return 1

ret = test_tenant_disable('test_create_tenant')
exit(ret)
