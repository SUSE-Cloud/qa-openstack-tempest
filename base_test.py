#!/usr/bin/python

import httplib2
import json
from glanceclient import Client
from tempest.common.utils.data_utils import rand_name
from tempest import openstack
import time

class BaseTest(object):

    def __init__(self):
        self.os = openstack.Manager()
        self.servers_client = self.os.servers_client
        self.images_client = self.os.images_client
        self.flavors_client = self.os.flavors_client
        self.volumes_client = self.os.volumes_client
        self.volumes_service = 'volume'
        self.config = self.os.config

        self.username = self.config.compute_admin.username
        self.password = self.config.compute_admin.password
        self.tenant_name = self.config.compute_admin.tenant_name

        self.flavor_ref = self.config.compute.flavor_ref
        
        self.base_url = 'http://' + self.config.identity.host + ':' + self.config.identity.port \
                        + '/' + self.config.identity.api_version + '/' + self.config.identity.path

    def _get_token_response(self):
        """ Get base token response """

        headers = {'content-type': 'application/json'}

        body = {
            "auth": {
                "passwordCredentials":{
                    "username": self.username,
                    "password": self.password,
                },
                "tenantName": self.tenant_name,
            },
        }
        http = httplib2.Http()
        response, content = http.request(self.base_url, 'POST',
                                        headers=headers,
                                        body=json.dumps(body))

        res_body = json.loads(content)

        return res_body

    def get_user_token(self):
        """ Get user token"""
    
        res_body = self._get_token_response()

        return res_body['access']['token']['id']

    def get_service_endpoint(self, service):
        """ Get service endpoint """

        res_body = self._get_token_response()

        for index in range(0, len(res_body['access']['serviceCatalog'])):
            if res_body['access']['serviceCatalog'][index]['name'] == service:
                return res_body['access']['serviceCatalog'][index]['endpoints'][0]['adminURL']

        return -1

    def upload_glance_image(self, file, disk_format='raw', container_format='bare'):
        """ Upload glance image file """

        token = self.get_user_token()
        endpoint = self.get_service_endpoint('glance')
        endpoint = endpoint.rsplit('/', 1)[0]

        glance = Client('1', endpoint, token)

        image_name = rand_name('jeos_')
        image = glance.images.create(name=image_name, disk_format=disk_format, container_format=container_format)
        image.update(data=open(file, 'rb'))

        return image.id

    def clean_servers(self):
        resp, body = self.servers_client.list_servers()

        for index in range(0, len(body['servers'])):
            server_id = body['servers'][index]['id']
            self.servers_client.delete_server(server_id)

        time.sleep(10)

        resp, body = self.servers_client.list_servers()

        if(len(body['servers'])):
            return -1
        else:
            return 0

    def clean_images(self):
        resp, images = self.images_client.list_images()
    
        for index in range(0, len(images)):
            image_id = images[index]['id']
            image_name = images[index]['name']
            
            if(image_name.startswith('jeos_')):
                self.images_client.delete_image(image_id)

        resp, images = self.images_client.list_images()

        if(len(images)):
            return -1
        else:
            return 0

    def _delete_flavor(self, flavor_id):
        endpoint = self.get_service_endpoint('nova')
        endpoint = endpoint + '/flavors/' + str(flavor_id)

        token = self.get_user_token()
        headers = {'X-Auth-Token': token}

        http = httplib2.Http()
        response, content = http.request(endpoint, 'DELETE', headers=headers)

        if(response['status'] == '202'):
            return 0

        return -1

    def clean_flavors(self):
        pass
        #resp, flavors = self.flavors_client.list_flavors()
        #
        #for index in range(0, len(flavors)):
        #    flavor_id = flavors[index]['id']
        #    print flavor_id

        #    #Can not delete flavors so far
        #    #if(flavor_id == '7'):
        #    #    self._delete_flavor(flavor_id)

    def clean_snapshots(self):

        endpoint = self.get_service_endpoint('nova-volume')
        endpoint = endpoint + '/snapshots'

        token = self.get_user_token()

        headers = {'X-Auth-Token': token}
    
        http = httplib2.Http()
        response, content = http.request(endpoint, 'GET', headers=headers)

        snapshots = json.loads(content)

        print (snapshots['snapshots'])

        for index in range(0, len(snapshots['snapshots'])):
            print snapshots['snapshots'][index]['id']
            endpoint = endpoint + '/' + snapshots['snapshots'][index]['id']
            response, content = http.request(endpoint, 'DELETE', headers=headers)

    def clean_volumes(self):
        resp, volumes = self.volumes_client.list_volumes()
        
        for index in range(0, len(volumes)):
            volume_id = volumes[index]['id']
            self.volumes_client.delete_volume(volume_id)

        time.sleep(120)

        resp, volumes = self.volumes_client.list_volumes()

        if(len(volumes)):
            return -1
        return 0

if __name__ == '__main__':

    bt = BaseTest()

    #bt.clean_servers()
    #bt.clean_images()
    #bt.clean_volumes()
    #bt.clean_snapshots()
    #bt.get_user_token()
    #bt.delete_flavor(7)

