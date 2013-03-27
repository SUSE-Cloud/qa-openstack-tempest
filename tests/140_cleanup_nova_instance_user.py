#!/usr/bin/python

import sys
sys.path.append('./')

from base_test import BaseTest
           
def test_cleanup_nova_instance_user(username, password, tenant_name, server_name):
    """ test a user to delete a server """

    user_bt = BaseTest(username, password, tenant_name)

    server = user_bt.get_server_by_name(server_name)
    if server == None: 
        return 3

    response, content = user_bt.clean_servers(server_name)
    if response['status'] == '204':
        return 0

    return 1

ret = test_cleanup_nova_instance_user('test_create_user', 'crowbar', 'test_create_tenant', 'jeos_01')
exit(ret)
