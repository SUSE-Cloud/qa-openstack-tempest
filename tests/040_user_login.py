#!/usr/bin/python

import sys
sys.path.append('/home/yaojia/tempest.essex')
sys.path.append('/home/yaojia/tempest.essex/qa-openstack-tempest')

from base_test import BaseTest

def test_login_by_username(username, password, tenant_name):
    """ test a user whose name is giving name to login first time """

    bt_user = BaseTest(username, password, tenant_name)
    resp, body = bt_user.servers_client.list_servers()

    if resp['status'] == '200':
        return 0
    return 1


ret = test_login_by_username('test_create_user', 'crowbar', 'test_create_tenant')
exit(ret)

