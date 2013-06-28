#!/usr/bin/python

import sys
import os

sys.path.append('./')
from glanceclient import Client
from base_test import BaseTest
import time
import os

def upload_glance_remote_image(file_path, disk_format='raw', container_format='bare', image_name='jeos_remote', timeout=60):
    """ Upload remote glance image file """

    baseTest = BaseTest()
    token = baseTest.token
    endpoint = baseTest.get_service_endpoint('glance')
    endpoint = endpoint.rsplit('/', 1)[0]

    glance = Client('1', endpoint = endpoint, token = token)
    meta = {
        'name': image_name,
        'is_public': True,
        'disk_format': disk_format,
        'container_format': container_format,
        'copy_from': file_path,
    }

    print 'file_path = ', file_path

    start = int(time.time())
    results = glance.images.create(**meta)

    print 'results = ', results

    image_id = results.id
   
    ret = baseTest._wait_for_image_status(image_id, 'ACTIVE', 1200)

    image_file = "/var/lib/glance/images/" + image_id
    # Ensure the image has been realy stroed in the glance location
    if ret == 0 and os.path.isfile(image_file):
        # clean the created image
        baseTest.clean_images(image_name)
        return 0
    return 1

def test_glance_import_remote_image(file_path, disk_format='raw', container_format='bare'):
    """ test administrator can deploy a glance image """
    return upload_glance_remote_image(file_path, 'raw', 'bare', 'jeos_remote', 120)

file_path = os.environ.get('IMAGE_FILE_REMOTE_PATH')
ret = test_glance_import_remote_image(file_path)
exit(ret)
