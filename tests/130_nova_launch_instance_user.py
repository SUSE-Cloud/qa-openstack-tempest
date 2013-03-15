#!/usr/bin/python

import sys
sys.path.append('/home/yaojia/tempest.essex')
sys.path.append('/home/yaojia/tempest.essex/qa-openstack-tempest')

from base_test import BaseTest
           
def test_nova_launch_instance_user(username, password, tenant_name, server_name, image_name, flavor_id):
    """ test a user to create server by uploading image file and tiny flavor """

    user_bt = BaseTest(username, password, tenant_name)
    image = user_bt.get_image_by_name(image_name)

    if image == None:
        return 3
    image_id = image['id']

    resp, server = user_bt.servers_client.create_server(server_name, image_id, flavor_id)

    return user_bt._wait_for_server_status(server['id'], 'ACTIVE', 180)

ret = test_nova_launch_instance_user('test_create_user', 'crowbar', 'test_create_tenant', 'jeos_01', 'jeos_01', 1)
exit(ret)
