#!/usr/bin/python

import sys
sys.path.append('/home/yaojia/tempest.essex')
sys.path.append('/home/yaojia/tempest.essex/qa-openstack-tempest')

from base_test import BaseTest
import time
           
def test_nova_launch_instance_cycle(username, password, tenant_name, image_name, flavor_id, cycle_number, timeout):
    """ test a user to teminate a creating server for times in a specific time period """

    user_bt = BaseTest(username, password, tenant_name)
    image = user_bt.get_image_by_name(image_name)

    if image == None:
        return 3

    image_id = image['id']

    server_name = 'test_cycle'

    for i in range(0, cycle_number):
        resp, server = user_bt.servers_client.create_server(server_name, image_id, flavor_id)
        resp, body = user_bt.servers_client.delete_server(server['id'])

        start = int(time.time())
        while(server != None):
            time.sleep(5)
            timed_out = int(time.time()) - start >= timeout

            if timed_out:
                return 1
            
            server = user_bt.get_server_by_name(server_name)

    return 0

test_nova_launch_instance_cycle('test_create_user', 'crowbar', 'test_create_tenant', 'jeos_01', 1, 3, 60)

