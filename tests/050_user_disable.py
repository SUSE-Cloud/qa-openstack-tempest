#!/usr/bin/python

import sys
sys.path.append('/home/yaojia/tempest.essex')
sys.path.append('/home/yaojia/tempest.essex/qa-openstack-tempest')

import json
from base_test import BaseTest
          
def test_disable_user(username):
    """ test administrator to disable a ueser by giving user name """

    bt = BaseTest()
    user = bt.get_user_by_name(username)

    if(user == None):
        return 3

    user_id = user['id']

    endpoint = bt.get_service_endpoint('keystone')
    endpoint = endpoint + '/users/' + user_id + '/enabled'

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    body = {
            'user': {
                'enabled': False,
            },
        }

    response, content = bt.put(endpoint, headers=headers, body=json.dumps(body))    

    if(response['status'] != '200'):
        return 1

    return 0

ret = test_disable_user('test_create_user')
exit(ret)

