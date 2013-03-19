#!/usr/bin/python

import sys
sys.path.append('./')

from base_test import BaseTest
 
def test_nova_launch_instance_admin(server_name, image_name, flavor_id):
    """ test a administrato to create server by uploading image file and tiny flavor """

    bt_admin = BaseTest()
    image = bt_admin.get_image_by_name(image_name)

    if image == None:
        return 3

    image_id = image['id']
    resp, server = bt_admin.servers_client.create_server(server_name, image_id, flavor_id)

    return bt_admin._wait_for_server_status(server['id'], 'ACTIVE', 180)

ret = test_nova_launch_instance_admin('jeos_admin', 'jeos_01', 1)
exit(ret)
