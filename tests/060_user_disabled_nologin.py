#!/usr/bin/python

import sys
sys.path.append('/home/yaojia/tempest.essex')
sys.path.append('/home/yaojia/tempest.essex/qa-openstack-tempest')

from base_test import BaseTest
from tempest import exceptions

def test_user_disabled_nologin(username, password, tenant_name):
    """ test a disabled user can not to login anymore """

    bt = BaseTest()
    user = bt.get_user_by_name(username)

    if(user == None):
        return 3

    try:
        bt_user = BaseTest(username, password, tenant_name)
    except exceptions.AuthenticationFailure:
        return 0

    return 1

ret = test_user_disabled_nologin('test_create_user', 'crowbar', 'test_create_tenant')
exit(ret)

