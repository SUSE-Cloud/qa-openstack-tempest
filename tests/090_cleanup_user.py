#!/usr/bin/python

import sys
sys.path.append('./')

from base_test import BaseTest

def test_delete_user(username):
    """ test administrator to delete a user whose name is the giving name"""

    bt = BaseTest()
    user = bt.get_user_by_name(username)

    if(user == None):
        return 3

    user_id = user['id']

    endpoint = bt.get_service_endpoint('keystone')
    endpoint = endpoint + '/users/' + user_id

    response, content = bt.delete(endpoint)    

    if(response['status'] == '200'):
        return 0

    return 1

test_delete_user('test_create_user')

