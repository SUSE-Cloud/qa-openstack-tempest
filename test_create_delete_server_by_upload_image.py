#!/usr/bin/python

import sys
sys.path.append('TEMPESTDIR')

import httplib2
import json
from glanceclient import Client
from tempest.common.utils.data_utils import rand_name
from tempest import openstack
import base_test
import time

class ServersTest(object):

    def __init__(self):
        self.os = openstack.Manager()
        self.servers_client = self.os.servers_client
        self.baseTest = base_test.BaseTest()
        self.flavor_ref = 1

    def upload_glance_image(self, file, disk_format='raw', container_format='bare'):
        """ Upload glance image file """

        token = self.baseTest.get_user_token()
        endpoint = self.baseTest.get_service_endpoint('glance')
        endpoint = endpoint.rsplit('/', 1)[0]

        glance = Client('1', endpoint, token)

        image_name = rand_name('jeos_')
        image = glance.images.create(name=image_name, disk_format=disk_format, container_format=container_format)
        image.update(data=open(file, 'rb'))

        return image.id

    def _wait_for_server_status(self, server_id, status, timeout=60):
        """Waits for a server to reach a given status"""

        resp, body = self.servers_client.get_server(server_id)
        server_status = body['status']
        start = int(time.time())

        while(server_status != status):
            time.sleep(10)
            resp, body = self.servers_client.get_server(server_id)
            server_status = body['status']

            print '.',

            if server_status == 'ERROR':
                print "Server status reruen error! FAILED!!!"
                return -1

            timed_out = int(time.time()) - start >= timeout

            if server_status != status and timed_out:
                message = 'Server %s failed to reach %s status within the \
                required time (%s s).' % (server_id, status,
                                          timeout)
                message += ' Current status: %s.' % server_status
                print message
                return -1
        return 0

           
    def test_create_server_by_upload_image_flavor(self, file, disk_format='raw', container_format='bare'):
        """ test creating server by uploading image file and tiny flavor """

        image_ref = self.upload_glance_image(file, disk_format=disk_format, container_format=container_format)

        server_name = rand_name('jeos_')

        resp, server = self.servers_client.create_server(server_name, image_ref, self.flavor_ref)

        #self.servers_client.wait_for_server_status(server['id'], 'ACTIVE')
        return self._wait_for_server_status(server['id'], 'ACTIVE', 180)

    def test_delete_server_by_name(self, name='jeos_'):
        """ test delete server by given name prefix """

        resp, body = self.servers_client.list_servers()

        for index in range(0, len(body['servers'])):
            if(body['servers'][index]['name'].startswith(name)):
                server_id = body['servers'][index]['id']
                self.servers_client.delete_server(server_id)

        time.sleep(30)

        resp, body = self.servers_client.list_servers()
        for index in range(0, len(body['servers'])):
            if(body['servers'][index]['name'].startswith(name)):
                return -1

        return 0

if __name__ == '__main__':

    st = ServersTest()
    file = "/home/yaojia/openSUSE_11.4_JeOS.i686-0.0.1.raw"

    print "test creating server by iploading image",
    ret = st.test_create_server_by_upload_image_flavor(file, disk_format='raw', container_format='bare')

    if ret != 0:
        print " false"
    else:
        print " ok"

    print "test delete server by give name prefix"
    ret = st.test_delete_server_by_name()
    
    if ret != 0:
        print " false"
    else:
        print " ok"

