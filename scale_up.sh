#!/bin/bash

echo "Preparing image..."
imgid=$(glance --insecure image-list --name jeos1 --status active | grep jeos1 | awk '{print $2}')

if [ "$imgid" == "" ] ; then
  echo "Creating image..."

  glance --insecure image-create --name=jeos1 --is-public=True \
         --container-format=bare --disk-format=qcow2 \
         --property hypervisor_type=kvm \
         --copy-from http://clouddata.cloud.suse.de/images/jeos-64.qcow2

  imgid=$(glance --insecure image-list --name jeos1 --status active | grep jeos1 | awk '{print $2}')

fi

if [ "$imgid" != "" ] ; then

  echo "Image successfully created. { $imgid }"

  echo "Launching VMs..."

  for i in {0..99}; do

    tenant="tenant_$i"
    echo "Creating tenant $tenant..."

    keystone tenant-create --name $tenant --description temporary --enabled true
    if [ "$?" == "0" ]; then

      user="user_$i"
      echo "Creating user $user..."

      tenantid=$(keystone --insecure tenant-list | grep $tenant | awk '{print $2}')

      keystone user-create --name $user --tenant-id $tenantid --pass 12345678 --email tux@suse.de --enabled true

      if [ "$?" == "0" ]; then

        for j in {0..9}; do

          instance="jeos_$i$j"
          inst_id=`nova --insecure --os_username $user --os_password 12345678 --os_tenant $tenant boot --flavor 1 --image $imgid $instance`
          rc=$?
          echo "Instance $instance created ($rc)"

        done

      else
        echo "Failed to create the user $user."
      fi
    else
      echo "Failed to create the tenant $tenant."
    fi

    echo "-----------------------------------------------------------------"

  done

else
  echo "Failed to create VM image."
fi

echo "Complete."
