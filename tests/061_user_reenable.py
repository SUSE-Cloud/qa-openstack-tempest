#!/usr/bin/python

import sys
sys.path.append('./')

import json
from base_test import BaseTest
         
def test_user_reenable(username):
    """ test enable a user who was disabled """

    bt = BaseTest()
    user = bt.get_user_by_name(username)

    if(user == None):
        return 3

    user_id = user['id']

    endpoint = bt.get_service_endpoint('keystone')['adminURL']
    endpoint = endpoint + '/users/' + user_id + '/enabled'

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    body = {
            'user': {
                'enabled': True,
            },
        }

    response, content = bt.put(endpoint, headers=headers, body=json.dumps(body));
    
    if(response['status'] != '200'):
        print "Reenable user failed!"
        return 1

    return 0

ret = test_user_reenable('test_create_user')
exit(ret)
