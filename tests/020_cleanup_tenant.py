#!/usr/bin/python

import sys
sys.path.append('/home/yaojia/tempest.essex')
sys.path.append('/home/yaojia/tempest.essex/qa-openstack-tempest')

from base_test import BaseTest
           
def test_delete_tenant_by_name(name):
    """ test administrator to delete a tenant whose name is the giving name"""
    bt = BaseTest()

    tenant = bt.get_tenant_by_name(name)

    if(tenant == None):
        print 'the tenant named %s is not existed!, skipped' %name
        return 3

    tenant_id = tenant['id']

    endpoint = bt.get_service_endpoint('keystone')
    endpoint = endpoint + '/tenants/' + tenant_id

    response, content = bt.delete(endpoint)

    if(response['status'] == '204'):
        return 0
    
    return 1

ret = test_delete_tenant_by_name('test_create_tenant')
exit(ret)
