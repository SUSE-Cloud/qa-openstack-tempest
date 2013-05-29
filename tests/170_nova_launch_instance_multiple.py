#!/usr/bin/python

import sys
import os
sys.path.append('./')

from base_test import BaseTest
           
def test_nova_launch_instance_multiple(username, password, tenant_name, image_name, flavor_id, number):
    """ test a user to create multiple servers with a same image """

    bt_user = BaseTest(username, password, tenant_name)
    image = bt_user.get_image_by_name(image_name)

    if image == None:
        return 3

    image_id = image['id']

    server_ids = list()
    for i in range(0, number):
        server_name = 'test_' + str(i)
        resp, server = bt_user.servers_client.create_server(server_name, image_id, flavor_id)
        server_ids.append(server['id'])

    ret = 0
    for server_id in server_ids:
        ret += bt_user._wait_for_server_status(server_id, 'ACTIVE', 600)

    if(ret > 0):
        return 1

    bt_user.clean_servers('test_', True)
    return 0

number = os.environ.get('MULTI_INST_COUNT')
if(number != None):
    number = int(number)
else:
    number = 3
ret = test_nova_launch_instance_multiple('test_create_user', 'crowbar', 'test_create_tenant', 'jeos_01', 1, number)
exit(ret)

