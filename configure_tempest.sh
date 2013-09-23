#!/bin/bash

# set environment
. ~/.openrc

# move run_tests.sh out of the way
echo "Disabling run_tests.sh..."
chmod 644 run_tests.sh
mv run_tests.sh run_tests.sh.bk

CONF_PATH=~/tempest/etc/tempest.conf

echo "Setting the config path to $CONF_PATH..."

cp "$CONF_PATH.sample" $CONF_PATH

echo "Checking for the test images..."
IMG1=$(glance image-list | grep 'jeos-64' | awk '{print $2}')
IMG2=$(glance image-list | grep 'SP2-64' | awk '{print $2}')

if [ "$IMG1" = "" ]; then
  echo "Retrieving a JEOS-64 image..."
  glance image-create --name=jeos-64 --is-public=True --container-format=bare --disk-format=qcow2 --property hypervisor_type=kvm --copy-from http://clouddata.cloud.suse.de/images/jeos-64.qcow2
  IMG1=$(glance image-list | grep 'jeos-64' | awk '{print $2}')
else
  echo "JEOS_64 image already in place."
fi

if [ "$IMG2" = "" ]; then
  echo "Retrieving SLES_SP2_x86_64 image ..."
  glance image-create --name=SP2-64 --is-public=True --container-format=bare --disk-format=qcow2 --property hypervisor_type=kvm --copy-from http://clouddata.cloud.suse.de/images/SP2-64up.qcow2
  IMG2=$(glance image-list | grep 'SP2-64' | awk '{print $2}')
else
  echo "SLES_SP2_x86_64 image already in place."
fi

# upload some test images
# KVM images
# glance image-create --name=jeos-64 --is-public=True --container-format=bare --disk-format=qcow2 --copy-from http://clouddata.cloud.suse.de/images/jeos-64.qcow2
# glance image-create --name=SP2-64 --is-public=True --container-format=bare --disk-format=qcow2 --copy-from http://clouddata.cloud.suse.de/images/SP2-64up.qcow2

# ...alternatively Xen (HVM) images
# glance image-create --name=jeos-64-hvm --is-public=True --container-format=bare --disk-format=qcow2 --property vm_mode=hvm --copy-from http://clouddata.cloud.suse.de/images/jeos-64.qcow2
# glance image-create --name=SP2-64 --is-public=True --container-format=bare --disk-format=qcow2 --property vm_mode=hvm --copy-from http://clouddata.cloud.suse.de/images/SP2-64up.qcow

# ... or Xen (PV) images
# glance image-create --name=jeos-64-pv --is-public=True --container-format=bare --disk-format=qcow2 --property vm_mode=xen --copy-from http://clouddata.cloud.suse.de/images/jeos-64-pv.qcow2

# extract the image IDs

echo "Image 1 has ID $IMG1"
echo "Image 2 has ID $IMG2"

echo "Copying image IDs into the configuration file..."
# substitute these image IDs into the tempest.conf file
sed -i -e "s/image_ref = .*/image_ref = $IMG1/" $CONF_PATH
sed -i -e "s/image_ref_alt = .*/image_ref_alt = $IMG2/" $CONF_PATH

# only necessary for HTTPS ------------>
#host_name=$(hostname -f)
#echo "Copying hostname ($host_name) into configuration..."
#sed -i -e "s\uri = http://127.0.0.1:5000/v2.0/\uri = https://$host_name:5000/v2.0/\g" $CONF_PATH
#sed -i -e "s\ec2_url = http://localhost:8773/services/Cloud\ec2_url = https://$host_name:8773/services/Cloud\g" $CONF_PATH
#sed -i -e "s\s3_url = http://localhost:3333\s3_url = https://$host_name:3333\g" $CONF_PATH

echo "Modifying the admin settings..."
# modify the admin settings in the tempest.conf file also to the default for SUSE Cloud 2.0
sed -i -e "s/admin_password = .*/admin_password = crowbar/g" $CONF_PATH
sed -i -e "s/admin_tenant_name = .*/admin_tenant_name = openstack/g" $CONF_PATH

#echo "Adjusting the build timeout..."
# increase the build timeout in the tempest.conf file
#sed -i -e "s/build_timeout = 600/build_timeout = 1500/g" $CONF_PATH

echo "Setting the correct database URI in the tempest.conf file..."
DB_URI=$(grep -i '^sql_connection=' /etc/nova/nova.conf | sed 's/sql_connection=//g')
PREDECESSOR=$(grep -i 'db_uri =' ~/tempest/etc/tempest.conf)

echo "Substituting \"$PREDECESSOR\" with \"db_uri = $DB_URI\"..."

sed -i "s|$PREDECESSOR|db_uri = $DB_URI|g" $CONF_PATH

# quantum
echo "Setting flag to indicate that Quantum is available..."
sed -i -e "s/quantum_available = .*/quantum_available = true/g" $CONF_PATH

echo "Querying for the public_network_id..."
public_network_id=$(quantum net-list | grep 'floating' | awk '{print $2}')

if [ "$public_network_id" != "" ] ; then
  echo "Configuring the public_network_id with $public_network_id ..."
  sed -i -e "s/public_network_id = .*/public_network_id = $public_network_id/g" $CONF_PATH
else
  echo "Unable to access the public_network_id."
fi

echo "Querying for the public_router_id..."
public_router_id=$(quantum router-list | grep "$public_network_id" | awk '{print $2}')

if [ "$public_router_id" != "" ] ; then
  echo "Configuring the public_router_id with $public_router_id ..."
  sed -i -e "s/public_router_id = .*/public_router_id = $public_router_id/g" $CONF_PATH
else
  echo "Unable to access the public_router_id."
fi

echo "Modifying the bin_dir path..."
sed -i -e "s|bin_dir = /usr/local/bin|bin_dir = /usr/bin|g" $CONF_PATH

echo "Modifying the path_to_private_key..."
sed -i -e "s|path_to_private_key = /home/user/.ssh/id_rsa|path_to_private_key = /root/.ssh/id_rsa|g" $CONF_PATH

echo "Querying for EC2 credentials..."
ec2_credentials=$( keystone ec2-credentials-list | grep admin | sed -e "s/ //g" | cut -d"|" -f 3,4 )
ec2_user=$(echo $ec2_credentials | cut -d"|" -f 1)
ec2_pass=$(echo $ec2_credentials | cut -d"|" -f 2)

if [ "$ec2_user" == "" ] ; then
  echo "aws_access key unavailable."
elif [ "$ec2_pass" == "" ] ; then
  echo "aws_secret is unavailable."
else
  echo "Found EC2 credentials, now writing them to the config."
  sed -i -e "s/aws_access =.*/aws_access = $ec2_user/g" $CONF_PATH
  sed -i -e "s/aws_secret =.*/aws_secret = $ec2_pass/g" $CONF_PATH
fi

# see Bug #830568 - Changing the server password causes errors in Tempest
echo "Setting change_password_available to false... (no KVM support)"
sed -i -e "s/change_password_available=true/change_password_available=false/g" $CONF_PATH

echo "Preparing config for live migration..."
sed -i -e "s/live_migration_available = false/live_migration_available = true/g" $CONF_PATH
sed -i -e "s/use_block_migration_for_live_migration = false/use_block_migration_for_live_migration = true/g" $CONF_PATH

# prepare some tenants
echo "Preparing new tenants..."

# get the tenant IDs
DEMO=$(keystone tenant-list | grep '^|\s[[:xdigit:]]*\s*|\s*demo\s*|\s*True\s*|\s*$' | sed 's/|\s//g' | awk '{print $1}')
ALT_DEMO=$(keystone tenant-list | grep '^|\s[[:xdigit:]]*\s*|\s*alt_demo\s*|\s*True\s*|\s*$' | sed 's/|\s//g' | awk '{print $1}')

if [ "$DEMO" = "" ]; then
  echo "Adding the tenant \"demo\""
  keystone tenant-create --name demo
  DEMO=$(keystone tenant-list | grep '^|\s[[:xdigit:]]*\s*|\s*demo\s*|\s*True\s*|\s*$' | sed 's/|\s//g' | awk '{print $1}')
else
  echo "Tenant \"demo\" already there."
fi

if [ "$ALT_DEMO" = "" ]; then
  echo "Adding the tenant \"alt_demo\""
  keystone tenant-create --name alt_demo
  ALT_DEMO=$(keystone tenant-list | grep '^|\s[[:xdigit:]]*\s*|\s*alt_demo\s*|\s*True\s*|\s*$' | sed 's/|\s//g' | awk '{print $1}')
else
  echo "Tenant \"alt_demo\" already there."
fi

echo "Tenant \"demo\" has ID $DEMO"
echo "Tenant \"alt_demo\" has ID $ALT_DEMO"

echo "Creating some users..."
# create some users

# check if the users are there before adding them
USR_1=$(keystone user-list | grep -i ' demo ')
USR_2=$(keystone user-list | grep -i ' alt_demo ')

if [ "$USR_1" = "" ]; then
  echo "Adding user \"demo\"..."
  keystone user-create --name demo --tenant-id $DEMO --pass secret --enabled true
else
  echo "User \"demo\" already there."
fi

if [ "$USR_2" = "" ]; then
  echo "Adding user \"alt_demo\"..."
  keystone user-create --name alt_demo --tenant-id $ALT_DEMO --pass secret --enabled true
else
  echo "User \"alt_demo\" already there."
fi

echo "Finished."
