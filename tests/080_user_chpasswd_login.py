#!/usr/bin/python

import sys
sys.path.append('./')

import json
from base_test import BaseTest
from keystoneclient.v2_0.users import UserManager

def change_user_password(username, password, tenant_name, newpassword):
    """ Change a user can change its password """

    bt = BaseTest()
    user = bt.get_user_by_name(username)
    if user == None:
        return 3

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    endpoint = bt.get_service_endpoint('keystone')['internalURL']
    endpoint = endpoint + '/OS-KSCRUD/users/' + user['id']

    bt_user = BaseTest(username, password, tenant_name)
    
    post_body = {
                "user": {
                    "password": newpassword,
                    "original_password": password,
                    }
                }

    response, content = bt_user.patch(endpoint, headers=headers, body=json.dumps(post_body))

    if(response['status'] != '200'):
        return 1
    return 0

def test_user_chpasswd_login(username, password, tenant_name, newpassword):
    """ test change a users password and the user can login with new password """

    ret = change_user_password(username, password, tenant_name, newpassword)

    if(ret != 0):
        return ret

    bt_user = BaseTest(username, newpassword, tenant_name)
    resp, body = bt_user.servers_client.list_servers()

    if resp['status'] != '200':
        return 1

    # restore the user's password
    return change_user_password(username, newpassword, tenant_name, password)

ret = test_user_chpasswd_login('test_create_user', 'crowbar', 'test_create_tenant', 'openstack')
exit(ret)
