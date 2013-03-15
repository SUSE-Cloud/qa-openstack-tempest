#!/usr/bin/python

import sys
sys.path.append('/home/yaojia/tempest.essex')
sys.path.append('/home/yaojia/tempest.essex/qa-openstack-tempest')

from base_test import BaseTest
from tempest import exceptions
     
def test_user_project_disabled_noaccess(username, password, tenant_name):
    """ test a user can not login anymore when its project is disabled """

    try:
        bt_user = BaseTest(username, password, tenant_name)
    except exceptions.AuthenticationFailure:
        return 0

    return 1

ret = test_user_project_disabled_noaccess('test_create_user', 'crowbar', 'test_create_tenant')
exit(ret)
