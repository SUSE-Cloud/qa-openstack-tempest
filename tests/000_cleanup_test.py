#!/usr/bin/python

import sys
sys.path.append('./')

from base_test import BaseTest

def delete_user(username):
    """ test administrator to delete a user whose name is the giving name"""

    bt = BaseTest()
    user = bt.get_user_by_name(username)

    if(user == None):
        print 'the user named %s is not existed!, skipped' %username
        return 3

    user_id = user['id']

    endpoint = bt.get_service_endpoint('keystone')['adminURL']
    endpoint = endpoint + '/users/' + user_id

    response, content = bt.delete(endpoint)    

    if(response['status'] == '200'):
        return 0

    return 1

def delete_tenant(name):
    """ test administrator to delete a tenant whose name is the giving name"""
    bt = BaseTest()

    tenant = bt.get_tenant_by_name(name)

    if(tenant == None):
        print 'the tenant named %s is not existed!, skipped' %name
        return 3

    tenant_id = tenant['id']

    endpoint = bt.get_service_endpoint('keystone')['adminURL']
    endpoint = endpoint + '/tenants/' + tenant_id

    response, content = bt.delete(endpoint)

    if(response['status'] == '204'):
        return 0

    return 1

def delete_image(name, regmode):
    bt = BaseTest()
    bt.clean_images(name, regmode)

def delete_server():
    bt = BaseTest()
    bt.clean_servers()

delete_server()
delete_user('test_create_user')
delete_tenant('test_create_tenant')
delete_image('jeos_', True)
