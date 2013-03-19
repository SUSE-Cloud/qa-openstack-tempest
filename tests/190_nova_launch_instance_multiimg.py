#!/usr/bin/python

import sys
sys.path.append('./')

from base_test import BaseTest
import time
           
def test_nova_launch_instance_multiimg(username, password, tenant_name, images_name, flavor_id, timeout):
    """ test a user to create multiple server with different images file """

    images_id = list()

    bt = BaseTest()
    user_bt = BaseTest(username, password, tenant_name)
    for image_name in images_name:
        image = bt.get_image_by_name(image_name)
        if(image == None):
            return 1
        images_id.append(image['id'])

    images_dict = dict(zip(images_name, images_id))

    for image_name in images_dict:
        server_name = 'jeos_' + image_name
        resp, server = user_bt.servers_client.create_server(server_name, images_dict[image_name], flavor_id)

        ret = user_bt._wait_for_server_status(server['id'], 'ACTIVE', timeout)
        if(ret != 0):
            return 1

    user_bt.clean_servers('jeos_', True)

    return 0

images_name = ['jeos_01', 'jeos_02']
ret = test_nova_launch_instance_multiimg('test_create_user', 'crowbar', 'test_create_tenant', images_name, 1, 180)
exit(ret)

