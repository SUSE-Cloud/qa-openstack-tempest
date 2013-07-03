#!/usr/bin/python

import sys
sys.path.append('./')

import json

from base_test import BaseTest
import time
           
def test_nova_change_quota_by_tenantname(tenant_name, key, value):
    """ test to change quotas of a tenant with a key and value """

    support_keys = ('metadata_items', 'injected_file_content_bytes', 'injected_files', 'gigabytes', 'ram',
                    'floating_ips',   'security_group_rules',        'instances',      'volumes',   'cores',
                    'id',             'security_groups')

    if key not in support_keys:
        return 2

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    bt = BaseTest()
    endpoint = bt.get_service_endpoint('nova')['adminURL']
    tenant = bt.get_tenant_by_name(tenant_name)

    body = {
        'quota_set': {
            key: value
        }
    }

    endpoint = endpoint + '/os-quota-sets/' + tenant['id']
    #response, content = bt.get(endpoint)
    
    response, content = bt.put(endpoint, headers, body=json.dumps(body))

    if response['status'] == '200':
        return 0
    return 1

ret = test_nova_change_quota_by_tenantname('test_create_tenant', 'instances', 20)
exit(ret)

