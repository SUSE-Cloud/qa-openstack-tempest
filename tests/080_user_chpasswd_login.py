#!/usr/bin/python

import sys
sys.path.append('./')

import json
from base_test import BaseTest

def change_user_password(username, password, tenant_name, newpassword):
    """ Change a user can change its password """

    bt = BaseTest()
    user = bt.get_user_by_name(username)
    if user == None:
        return 3

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    endpoint = bt.get_service_endpoint('keystone')
    endpoint = endpoint + '/users/' + user['id']

    bt_user = BaseTest(username, password, tenant_name)
    
    post_body = {
                'user': {
                    'id': user['id'],
                    'password': newpassword,
                }
            }

    response, content = bt_user.put(endpoint, headers=headers, body=json.dumps(post_body))

    if(response['status'] != '200'):
        return 1
    return 0

def test_user_chpasswd_login(username, password, tenant_name, newpassword):
    """ test change a users password and the user can login with new password """

    ret = change_user_password(username, password, tenant_name, newpassword)

    if(ret != 0):
        return ret

    bt = BaseTest()
    endpoint = bt.get_service_endpoint('nova')
    endpoint = endpoint + '/servers'

    bt_user = BaseTest(username, newpassword, tenant_name)
    response, content = bt_user.get(endpoint)

    # restore the user's password
    change_user_password(username, newpassword, tenant_name, password)

    if response['status'] == '200':
        return 0

    return 1

ret = test_user_chpasswd_login('test_create_user', 'crowbar', 'test_create_tenant', 'openstack')
exit(ret)
