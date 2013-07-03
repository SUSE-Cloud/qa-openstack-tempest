#!/usr/bin/python

import httplib2
import json

import sys
sys.path.append('../')
sys.path.append('/opt/stack/python-glanceclient')
from glanceclient import Client

from tempest.common.utils.data_utils import rand_name
from tempest import clients as openstack
from tempest import exceptions
import time

class BaseTest(object):

    def __init__(self, username=None, password=None, tenant_name=None):

        self.username = username or 'admin'
        self.password = password or 'crowbar'
        self.tenant_name = tenant_name or 'admin'

        self.os = openstack.Manager(self.username, self.password, self.tenant_name)
        self.servers_client = self.os.servers_client
        self.images_client = self.os.images_client
        self.flavors_client = self.os.flavors_client
        self.volumes_client = self.os.volumes_client
        self.config = self.os.config

        self.flavor_ref = self.config.compute.flavor_ref
        self.auth_url = self.os.auth_url

        self.token = self._get_user_token()

    def _wait_for_server_status(self, server_id, status, timeout=60):
        """Waits for a server to reach a given status"""

        resp, body = self.servers_client.get_server(server_id)
        server_status = body['status']
        start = int(time.time())

        while(server_status != status):
            time.sleep(10)
            resp, body = self.servers_client.get_server(server_id)
            server_status = body['status']

            if server_status == 'ERROR':
                print "Server status reruen error! FAILED!!!"
                return 1

            timed_out = int(time.time()) - start >= timeout

            if server_status != status and timed_out:
                message = 'Server %s failed to reach %s status within the \
                required time (%s s).' % (server_id, status,
                                          timeout)
                message += ' Current status: %s.' % server_status
                return 1
        return 0

    def _wait_for_image_status(self, image_id, status, timeout=60):
        resp, body = self.images_client.get_image(image_id)
        image_status = body['status']
        start = int(time.time())

        while image_status != status:
            time.sleep(10)
            resp, body = self.images_client.get_image(image_id)
            image_status = body['status']

            if image_status == 'ERROR':
                print "Image status reruen error! FAILED!!!"
                return 1

            timed_out = int(time.time()) - start >= timeout

            if image_status != status and timed_out:
                message = 'Image %s failed to reach %s status within the \
                required time (%s s).' % (image_id, status,
                                          timeout)
                message += ' Current status: %s.' % image_status
                return 1

        return 0

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
        token_url = self.auth_url + '/tokens'
    
        response, content = http.request(token_url, 'POST',
                                        headers=headers,
                                        body=json.dumps(body))

        if(response['status'] != '200'):
            return None

        res_body = json.loads(content)

        return res_body

    def _get_user_token(self):
        """ Get user token"""
    
        res_body = self._get_token_response()

        if res_body == None:
            return None

        return res_body['access']['token']['id']

    def get_tenant_by_name(self, name):
        endpoint = self.get_service_endpoint('keystone')['adminURL']
        endpoint = endpoint + '/tenants'

        response, content = self.get(endpoint)

        tenants = json.loads(content)

        tenant = None 
        for index in range(0, len(tenants['tenants'])):
            tenant_name = tenants['tenants'][index]['name']
            if(tenant_name == name):
                tenant = tenants['tenants'][index]

        return tenant

    def get_tenant_by_id(self, id):
        endpoint = self.get_service_endpoint('keystone')['adminURL']
        endpoint = endpoint + '/tenants'

        response, content = self.get(endpoint)

        tenants = json.loads(content)

        tenant = None
        for index in range(0, len(tenants['tenants'])):
            tenant_id = tenants['tenants'][index]['id']
            if(tenant_id == id):
                tenant = tenants['tenants'][index]

        return tenant

    def get_user_by_name(self, name):
        endpoint = self.get_service_endpoint('keystone')['adminURL']
        endpoint = endpoint + '/users'

        response, content = self.get(endpoint)

        users = json.loads(content)

        user = None
        for index in range(0, len(users['users'])):
            user_name = users['users'][index]['name']
            if(user_name == name):
                user = users['users'][index]

        return user

    def delete_user(self, user_id):

        endpoint = bt.get_service_endpoint('keystone')['adminURL']
        endpoint = endpoint + '/users/' + user_id

        response, content = self.delete(endpoint)

        if(response['status'] == '204'):
            return 0

        return 1

    def delete_mutiple_users(self, exception_list = None):
        endpoint = self.get_service_endpoint('keystone')['adminURL']
        endpoint = endpoint + '/users'

        response, content = self.get(endpoint)
        users = json.loads(content)

        for index in range(0, len(users['users'])):
            user_name = users['users'][index]['name']
            if((exception_list != None) and (user_name in exception_list)):
		            continue
	    
            user_id = users['users'][index]['id']
            if(self.delete_user(user_id)):
        	print "delete user: %s failed!" % user_name

    def delete_tenant(self, tenant_id):
        endpoint = bt.get_service_endpoint('keystone')['adminURL']
        endpoint = endpoint + '/tenants/' + tenant_id

        response, content = bt.delete(endpoint)

        if(response['status'] == '204'):
            return 0

        return 1

    def delete_multiple_tenants(self, exception_list = None):
        endpoint = self.get_service_endpoint('keystone')['adminURL']
        endpoint = endpoint + '/tenants'

        response, content = self.get(endpoint)
        tenants = json.loads(content)

        tenant = None
	for index in range(0, len(tenants['tenants'])):
            tenant_name = tenants['tenants'][index]['name']
	    if(exception_list != None):
                if(tenant_name in exception_list):
		    print "tenant: %s is in exception list" % tenant_name
		    continue
            print "tenant: %s is not in exception list, will be deleted!" % tenant_name
            tenant_id = tenants['tenants'][index]['id']
	    if(self.delete_tenant(tenant_id)):
	        print "delete tenant: %s failed!" % user_name

    def get_server_by_name(self, name):
        resp, body = self.servers_client.list_servers()

        server = None
        for index in range(0, len(body['servers'])):
            server_name = body['servers'][index]['name']
            if(server_name == name):
                server = body['servers'][index]

        return server

    def get_server_by_id(self, id):
        resp, body = self.servers_client.list_servers()

        server = None
        for index in range(0, len(body['servers'])):
            server_id = body['servers'][index]['id']
            if(server_id == id):
                server = body['servers'][index]

        return server

    def get_user_by_id(self, id):

        endpoint = self.get_service_endpoint('keystone')['adminURL']
        endpoint = endpoint + '/users'

        response, content = self.get(endpoint)

        users = json.loads(content)

        user = None
        for index in range(0, len(users['users'])):
            user_id = users['users'][index]['id']
            if(user_id == id):
                user = users['users'][index]

        return user
    
    def get_image_by_name(self, name):
        
        endpoint = self.get_service_endpoint('glance')['adminURL']
        endpoint = endpoint + '/images'

        response, content = self.get(endpoint)
        images = json.loads(content)

        image = None

        for index in range(0, len(images['images'])):
            image_name = images['images'][index]['name']
            if(image_name == name):
                image = images['images'][index]

        return image

    def get_image_by_id(self, id):
        endpoint = self.get_service_endpoint('glance')['adminURL']
        endpoint = endpoint + '/images'

        response, content = self.get(endpoint)

        images = json.loads(content)

        image = None

        for index in range(0, len(images['images'])):
            image_id = images['images'][index]['id']
            if(image_id == id):
                image = images['images'][index]

        return image

    def get_service_endpoint(self, service):
        """ Get service endpoint """

        endpoint = None
        res_body = self._get_token_response()

        endpoints = {}
        for index in range(0, len(res_body['access']['serviceCatalog'])):
            if res_body['access']['serviceCatalog'][index]['name'] == service:
                endpoints['adminURL'] = res_body['access']['serviceCatalog'][index]['endpoints'][0]['adminURL']
                endpoints['publicURL'] = res_body['access']['serviceCatalog'][index]['endpoints'][0]['publicURL']
                endpoints['internalURL'] = res_body['access']['serviceCatalog'][index]['endpoints'][0]['internalURL']

        #for openstack/grizzly, we need append glance version, for SUSE Cloud2.0, we needn't it
	    #if endpoint != None and service == 'glance':
		#    endpoint += '/v2'

        return endpoints

    def upload_glance_image(self, file, disk_format='raw', container_format='bare'):
        """ Upload glance image file """

        endpoint = self.get_service_endpoint('glance')['adminURL']
        endpoint = endpoint.rsplit('/', 1)[0]

        # version 2 seem not to support upload image
        glance = Client('1', endpoint = endpoint, token = self.token) 

        image_name = rand_name('jeos_')
        image = glance.images.create(name=image_name, disk_format=disk_format, container_format=container_format)
        image.update(data=open(file, 'rb'))

        return image.id

    def clean_servers(self, name=None, regmode=False, exception_list=None):

        resp = None
        meta = None
        search_opts = {'all_tenants':1}
        resp, body = self.servers_client.list_servers(search_opts)

        for index in range(0, len(body['servers'])):
            server_id = body['servers'][index]['id']
            server_name = body['servers'][index]['name']
            if((exception_list != None) and (server_name in exception_list)):
                continue
            if(name == None):
                resp, meta = self.servers_client.delete_server(server_id)
            else:
                if(regmode == False):
                    if(server_name == name):
                        resp, meta = self.servers_client.delete_server(server_id)
                else:
                    if(server_name.startswith(name)):
                        resp, meta = self.servers_client.delete_server(server_id)

            time.sleep(1)

        return resp, meta

    def clean_images(self, name=None, regmode=False):
        resp, images = self.images_client.list_images()
    
        for index in range(0, len(images)):
            image_id = images[index]['id']
            
            if(name == None):
                self.images_client.delete_image(image_id)
            else:
                image_name = images[index]['name']
                if(regmode == False):
                    if(image_name == name):
                        self.images_client.delete_image(image_id)
                else:
                    if(image_name.startswith(name)):
                        self.images_client.delete_image(image_id)

    def _delete_flavor(self, flavor_id):
        endpoint = self.get_service_endpoint('nova')['adminURL']
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

        endpoint = self.get_service_endpoint('cinder')['adminURL']
        endpoint = endpoint + '/snapshots'

        token = self._get_user_token()

        headers = {'X-Auth-Token': token}
    
        http = httplib2.Http()
        response, content = http.request(endpoint, 'GET', headers=headers)

        print content
        exit(0)

        snapshots = json.loads(content)

        for index in range(0, len(snapshots['snapshots'])):
            endpoint = endpoint + '/' + snapshots['snapshots'][index]['id']
            response, content = http.request(endpoint, 'DELETE', headers=headers)

    def clean_volumes(self):

        search_opts = {'all_tenants':1}
        resp, volumes = self.volumes_client.list_volumes(search_opts)
        
        for index in range(0, len(volumes)):
            volume_id = volumes[index]['id']
            self.volumes_client.delete_volume(volume_id)
            time.sleep(1)

        time.sleep(120)

        resp, volumes = self.volumes_client.list_volumes()

        if(len(volumes)):
            return -1
        return 0

    def post(self, url, headers, body):
        return self.request('POST', url, headers, body)

    def get(self, url):
        return self.request('GET', url)

    def delete(self, url):
        return self.request('DELETE', url)

    def put(self, url, headers, body):
        return self.request('PUT', url, headers, body)

    def patch(self, url, headers, body):
        return self.request('PATCH', url, headers, body)

    def request(self, method, url, headers=None, body=None, depth=0):
        """A simple HTTP request interface."""

        self.http_obj = httplib2.Http()
        if headers == None:
            headers = {}

        if(self.token == None):
            return None, None
        headers['X-Auth-Token'] = self.token

        req_url = url

        resp, resp_body = self.http_obj.request(req_url, method,
                          headers=headers, body=body)
        if resp.status == 401:
            raise exceptions.Unauthorized()

        if resp.status == 404:
            raise exceptions.NotFound(resp_body)

        if resp.status == 400:
            resp_body = json.loads(resp_body)
            raise exceptions.BadRequest(resp_body['badRequest']['message'])

        if resp.status == 409:
            resp_body = json.loads(resp_body)
            raise exceptions.Duplicate(resp_body)
        
        if resp.status == 413:
            resp_body = json.loads(resp_body)
            if 'overLimit' in resp_body:
                raise exceptions.OverLimit(resp_body['overLimit']['message'])
            elif depth < MAX_RECURSION_DEPTH:
                delay = resp['Retry-After'] if 'Retry-After' in resp else 60
                time.sleep(int(delay))
                return self.request(method, url, headers, body, depth + 1)
            else:
                raise exceptions.RateLimitExceeded(
                    message=resp_body['overLimitFault']['message'],
                    details=resp_body['overLimitFault']['details'])

        if resp.status in (500, 501):
            resp_body = json.loads(resp_body)
            #I'm seeing both computeFault and cloudServersFault come back.
            #Will file a bug to fix, but leave as is for now.

            if 'cloudServersFault' in resp_body:
                message = resp_body['cloudServersFault']['message']
            else:
                message = resp_body['computeFault']['message']
            raise exceptions.ComputeFault(message)

        if resp.status >= 400:
            resp_body = json.loads(resp_body)
            raise exceptions.TempestException(str(resp.status))

        return resp, resp_body

if __name__ == '__main__':

    bt = BaseTest()
    #user = bt.get_user_by_name('alt_demo')
    #print user

    #user = bt.get_user_by_id('ce205b61760c463cb46e41909de8495f')
    #print user
    #image = bt.get_image_by_name('cirros-0.3.1-x86_64-uec')
    #print image

    #image = bt.get_image_by_id(image['id'])

    #tenant = bt.get_tenant_by_name('demo')
    #print tenant

    #server = bt.get_server_by_name('ImagesWhiteboxTest-instance707177')
    #print server

    #bt.clean_servers()
    #bt.upload_glance_image('/home/yaojia/openSUSE_11.4_JeOS.i686-0.0.1.raw')
    #bt.clean_images('jeos_347771')   
    exception_user_list = ('admin', 'demo', 'cinder', 'alt_demo', 'glance', 'nova')
    bt.delete_mutiple_users(exception_user_list)

    exception_tenant_list = ('admin', 'alt_demo', 'demo', 'invisible_to_admin', 'service', 'openstack')
    bt.delete_multiple_tenants(exception_tenant_list)

    #print image

    #bt.clean_servers()
    #bt.clean_images()
    #bt.clean_volumes()
    #bt.clean_snapshots()
    #bt.get_user_token()
    #bt.delete_flavor(7)

