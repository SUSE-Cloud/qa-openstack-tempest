#!/bin/bash

echo "SUSE Cloud 4 - Tempest configuration for HTTP"

# set environment
. ~/.openrc

CONF_PATH=/etc/tempest/tempest.conf

echo "Setting the config path to $CONF_PATH..."

cp "/var/lib/openstack-tempest-test/etc/tempest.conf.sample" $CONF_PATH

echo "Checking for the test images..."
#IMG1=$(glance image-list | grep 'jeos-64' | awk '{print $2}')
#IMG2=$(glance image-list | grep 'SP2-64' | awk '{print $2}')
IMG1=$(glance image-list | grep 'cirros-0' | awk '{print $2}')
IMG2=$(glance image-list | grep 'cirros-1' | awk '{print $2}')
IMG3=$(glance image-list | grep 'fedora-0' | awk '{print $2}')

if [ "$IMG1" = "" ]; then
  echo "Retrieving a cirros-0 image..."
  glance image-create --name=cirros-0 --is-public=True --container-format=bare --disk-format=qcow2 --property hypervisor_type=kvm --copy-from http://clouddata.cloud.suse.de/images/cirros-0.3.1-x86_64-disk.qcow2
  IMG1=$(glance image-list | grep 'cirros-0' | awk '{print $2}')
else
  echo "cirros-0 image already in place."
fi

if [ "$IMG2" = "" ]; then
  echo "Retrieving the cirros-1 image ..."
  glance image-create --name=cirros-1 --is-public=True --container-format=bare --disk-format=qcow2 --property hypervisor_type=kvm --copy-from http://clouddata.cloud.suse.de/images/cirros-0.3.1-x86_64-disk.qcow2
  IMG2=$(glance image-list | grep 'cirros-1' | awk '{print $2}')
else
  echo "cirros-1 image already in place."
fi

if [ "$IMG3" = "" ]; then
  echo "Retrieving the fedora-0 image ..."
  glance image-create --name=fedora-0 --is-public=True --container-format=bare --disk-format=qcow2 --property hypervisor_type=kvm --copy-from http://download.fedoraproject.org/pub/fedora/linux/releases/20/Images/x86_64/Fedora-x86_64-20-20131211.1-sda.qcow2
  IMG3=$(glance image-list | grep 'fedora-0' | awk '{print $2}')
else
  echo "fedora-0 image already in place."
fi

# extract the image IDs

echo "Image 1 has ID $IMG1"
echo "Image 2 has ID $IMG2"
echo "Image 3 has ID $IMG3"

echo "Copying image IDs into the configuration file..."
# substitute these image IDs into the tempest.conf file
#sed -i -e "s/#image_ref=.*/image_ref=$IMG1/" $CONF_PATH
crudini --set $CONF_PATH compute image_ref $IMG1
#sed -i -e "s/#image_ref_alt=.*/image_ref_alt=$IMG2/" $CONF_PATH
crudini --set $CONF_PATH compute image_ref_alt $IMG2

# the fedora image is copied to the [orchestration] section
#sed -i -e "s/^#image_ref=.*$/image_ref=$IMG3/" $CONF_PATH
crudini --set $CONF_PATH orchestration image_ref $IMG3

echo "Making an image directory for cirros images for the [scenario] tests..."
mkdir -p ~/tempest/img
cd ~/tempest/img
echo "Getting the cirros images..."
wget http://download.cirros-cloud.net/0.3.1/cirros-0.3.1-x86_64-uec.tar.gz
echo "Unpacking the tarball..."
tar -xf cirros-0.3.1-x86_64-uec.tar.gz

# set the config
#sed -i -e "s|^#img_dir=.*$|img_dir = $(pwd)|g" $CONF_PATH
crudini --set $CONF_PATH scenario img_dir $(pwd)
cd ..

echo "Modifying the admin settings..."
# modify the admin settings in the tempest.conf file also to the default for SUSE Cloud 3
#sed -i -e "s/#admin_password=.*/admin_password=crowbar/g" $CONF_PATH
crudini --set $CONF_PATH identity admin_password crowbar
#sed -i -e "s/#admin_tenant_name=.*/admin_tenant_name=openstack/g" $CONF_PATH
crudini --set $CONF_PATH identity admin_tenant_name openstack

#echo "Adjusting the flavor instance_type to something that actually exists (m1.tiny)..."
#sed -i -e "s/instance_type = m1.micro/instance_type = m1.tiny/g" $CONF_PATH

echo "Checking for the flavor m1.micro..."
flavor=$(nova flavor-list | grep 'm1.micro')

if [ "$flavor" = "" ] ; then
  echo "Flavor m1.micro not found, so adding it as a new flavor..."
  nova flavor-create m1.micro 84 128 0 1
else
  echo "m1.micro already exists."
fi

echo "Changing the fixed_network_name..."
#sed -i -e "s/#fixed_network_name=.*/fixed_network_name=fixed/g" $CONF_PATH
crudini --set $CONF_PATH compute fixed_network_name fixed

echo "Querying for the public_network_id..."
public_network_id=$(neutron net-list | grep 'floating' | awk '{print $2}')

if [ "$public_network_id" != "" ] ; then
  echo "Configuring the public_network_id with $public_network_id ..."
  #sed -i -e "s/#public_network_id=.*/public_network_id=$public_network_id/g" $CONF_PATH
  crudini --set $CONF_PATH network public_network_id $public_network_id
else
  echo "Unable to access the public_network_id."
fi

echo "Querying for the public_router_id..."
public_router_id=$(neutron router-list | grep "$public_network_id" | awk '{print $2}')

if [ "$public_router_id" != "" ] ; then
  echo "Configuring the public_router_id with $public_router_id ..."
  #sed -i -e "s/#public_router_id=.*/public_router_id=$public_router_id/g" $CONF_PATH
  crudini --set $CONF_PATH network public_router_id $public_router_id
else
  echo "Unable to access the public_router_id."
fi

echo "Querying the fixed network UUID for the default network..."
default_network=$(neutron net-list | grep '|\sfixed\s\s*|' | awk '{print $2}')

if [ "$default_network" != "" ] ; then
  echo "Configuring the default_network with $default_network ..."
  #sed -i -e "s/#default_network=.*/default_network=$default_network/g" $CONF_PATH
  crudini --set $CONF_PATH network default_network $default_network
else
  echo "Unable to access fixed network UUID."
fi

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
  #sed -i -e "s/#aws_access=.*/aws_access=$ec2_user/g" $CONF_PATH
  crudini --set $CONF_PATH boto aws_access $ec2_user
  #sed -i -e "s/#aws_secret=.*/aws_secret=$ec2_pass/g" $CONF_PATH
  crudini --set $CONF_PATH boto aws_secret $ec2_pass
fi

echo "Adding new variable to [orchestration]..."
#sed -i -e 's/^\[orchestration\]$/&\nmax_template_size = 524288/g' $CONF_PATH
crudini --set $CONF_PATH orchestration nmax_template_size 524288

echo "Disabling change-password support..."
#sed -i -e "s/#change_password=.*/change_password=false/g" $CONF_PATH
crudini --set $CONF_PATH compute-feature-enabled change_password false

echo "Preparing config for live migration..."
#sed -i -e "s/#live_migration=.*/live_migration=true/g" $CONF_PATH
crudini --set $CONF_PATH compute-feature-enabled live_migration true
#sed -i -e "s/#block_migration_for_live_migration=.*/block_migration_for_live_migration=true/g" $CONF_PATH
crudini --set $CONF_PATH compute-feature-enabled block_migration_for_live_migration true

echo "Setting CLI directory..."
#sed -i -e "s\#cli_dir=.*\cli_dir=/usr/bin\g" $CONF_PATH
crudini --set $CONF_PATH cli cli_dir /usr/bin

echo "Setting available services..."
#sed -i -e "s/#cinder=true/cinder=true/g" $CONF_PATH
crudini --set $CONF_PATH service_available cinder true
#sed -i -e "s/#neutron=false/neutron=true/g" $CONF_PATH
crudini --set $CONF_PATH service_available neutron true
#sed -i -e "s/#glance=true/glance=true/g" $CONF_PATH
crudini --set $CONF_PATH service_available glance true
#sed -i -e "s/#swift=true/swift=true/g" $CONF_PATH
crudini --set $CONF_PATH service_available swift true
#sed -i -e "s/#nova=true/nova=true/g" $CONF_PATH
crudini --set $CONF_PATH service_available nova true
#sed -i -e "s/#heat=false/heat=true/g" $CONF_PATH
crudini --set $CONF_PATH service_available heat true
#sed -i -e "s/#ceilometer=true/ceilometer=true/g" $CONF_PATH
crudini --set $CONF_PATH service_available ceilometer true
#sed -i -e "s/#horizon=true/horizon=true/g" $CONF_PATH
crudini --set $CONF_PATH service_available horizon true

# additional options added for icehouse commented out config

#sed -i -e "s/#use_stderr=.*/use_stderr=false/g" $CONF_PATH
crudini --set $CONF_PATH DEFAULT use_stderr false
#sed -i -e "s/#log_file=.*/log_file=tempest.log/g" $CONF_PATH
crudini --set $CONF_PATH DEFAULT log_file tempest.log
#sed -i -e "s/#lock_path=.*/lock_path=/tmp/g" $CONF_PATH
crudini --set $CONF_PATH DEFAULT lock_path /tmp
#sed -i -e "s/#backup=.*/backup=falseg" $CONF_PATH
crudini --set $CONF_PATH volume-feature-enabled backup false

crudini --set $CONF_PATH volume storage_protocol iSCSI


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

echo "Allowing admin the admin rights to the tenant demo ..."
keystone user-role-add --user admin --role admin --tenant demo

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

# Removed for Icehouse does not support nose anymore
#echo "Adding the python-openstack.nose_plugin package..."
#zypper -n addrepo http://download.opensuse.org/repositories/Cloud:OpenStack:Havana/SLE_11_SP3/Cloud:OpenStack:Havana.repo
#zypper refresh
#zypper -n install python-openstack.nose_plugin

echo "Finished. Please modify /etc/tempest/tempest.conf storage_protocol option in [volume] section to reflect your current config (iSCSI, ceph, ...)"

