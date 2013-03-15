#!/usr/bin/python

import sys
sys.path.append('/home/yaojia/tempest.essex')
sys.path.append('/home/yaojia/tempest.essex/qa-openstack-tempest')

from base_test import BaseTest
from tempest import exceptions

def test_delete_user_nologin(username, password, tenant_name):
    """ test a user deleted can not login anymore """

    bt = BaseTest()

    try:
        bt_user = BaseTest(username, password, tenant_name)
    except exceptions.AuthenticationFailure:
        return 0

    return 1

test_delete_user_nologin('test_create_user', 'crowbar', 'openstack')

