#!/usr/bin/python

import sys
sys.path.append('./')

from base_test import BaseTest
           
def test_cleanup_nova_instance_admin(server_name):
    """ test a administrator to teminate the server whose name is giving name """

    bt = BaseTest()
    ret = bt.clean_servers(server_name)

ret = test_cleanup_nova_instance_admin('jeos_00')
exit(ret)

