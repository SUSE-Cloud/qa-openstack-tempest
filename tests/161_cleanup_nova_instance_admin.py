#!/usr/bin/python

import sys
sys.path.append('./')
sys.path.append('../')

from base_test import BaseTest
from tempest import exceptions
           
def test_nocleanup_nova_instance_admin_user(username, password, tenant_name, server_name):
    """ test a uer to teminiate a server created by administrator should fail """

    bt = BaseTest()
    server = bt.get_server_by_name(server_name)

    res, meta = bt.servers_client.delete_server(server['id'])

    if res['status'] == '204':
        return 0
    return 1

ret = test_nocleanup_nova_instance_admin_user('test_create_user', 'crowbar', 'test_create_tenant', 'jeos_admin')
exit(ret)

