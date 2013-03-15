#!/usr/bin/python

import sys
sys.path.append('/home/yaojia/tempest.essex')
sys.path.append('/home/yaojia/tempest.essex/qa-openstack-tempest')

from base_test import BaseTest
           
def test_nova_launch_instance_admin(server_name, image_name, flavor_id):
    """ test a administrator to create a server by uploading image file and tiny flavor """

    bt = BaseTest()
    image = bt.get_image_by_name(image_name)

    if image == None:
        return 3

    image_id = image['id']

    resp, server = bt.servers_client.create_server(server_name, image_id, flavor_id)

    return bt._wait_for_server_status(server['id'], 'ACTIVE', 180)

ret = test_nova_launch_instance_admin('jeos_00', 'jeos_01', 1)
exit(ret)

