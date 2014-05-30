#!/bin/bash

. ~/.openrc

echo "Terminating all instances..."

instances=$(nova list --all-tenants | grep '^|\s[[:xdigit:]].*$' | awk '{print $2}')

if [ "$instances" != "" ] ; then
  for inst in $instances; do
    echo "Deleting instance $inst ..."
    nova delete $inst
  done
else
  echo "No instances to delete."
fi

echo "Deleting all Tempest users..."

echo "Deleting the user \"demo\" ..."
keystone user-delete $(keystone user-list | grep '^.*|\s*demo\s*|.*$' | awk '{print $2}')

echo "Deleting the user \"alt_demo\" ..."
keystone user-delete $(keystone user-list | grep '^.*|\s*alt_demo\s*|.*$' | awk '{print $2}')

users=$(keystone user-list | grep '^.*-user\s*.*$' | awk '{print $2}')

if [ "$users" != "" ] ; then
  for usr in $users; do
    echo "Deleting user $usr ..."
    keystone user-delete $usr
  done
else
  echo "No users to delete."
fi

echo "Deleting all Tempest tenants..."

tenants=$(keystone tenant-list | grep '^.*-tenant\s*.*$' | awk '{print $2}')

echo "Deleting the tenant \"demo\" ..."
keystone tenant-delete $(keystone tenant-list | grep '^.*|\s*demo\s*|.*$' | awk '{print $2}')

echo "Deleting the tenant \"alt_demo\" ..."
keystone tenant-delete $(keystone tenant-list | grep '^.*|\s*alt_demo\s*|.*$' | awk '{print $2}')

if [ "$tenants" != "" ] ; then
  for tnt in $tenants; do
    echo "Deleting tenant $tnt ..."
    keystone tenant-delete $tnt
  done
else
  echo "No tenants to delete."
fi

echo "Deleting all Nova images..."
images=$(nova image-list | grep '^|\s[[:xdigit:]]*-[[:xdigit:]]*-[[:xdigit:]]*-[[:xdigit:]]*-[[:xdigit:]]*\s|.*$' | awk '{print $2}')

if [ "$images" != "" ] ; then
  for img in $images; do
    echo "Deleting image $img ..."
    nova image-delete $img
  done
else
  echo "No images to delete."
fi

echo "Deleting Neutron routers..."
routers=$(neutron router-list | grep -e '-router\s' | awk '{print $2}')

if [ "$routers" != "" ] ; then
  for router in $routers; do
    echo "Deleting router $router ..."
    neutron router-delete $router
  done
else
  echo "No routers to delete."
fi

echo "Deleting Neutron Networks..."
networks=$(neutron net-list | grep '-network\s' | awk '{print $2}')

if [ "$networks" != "" ] ; then
  for network in $networks; do
    echo "Deleting network $network ..."
    neutron net-delete $network
  done
else
  echo "No networks to delete."
fi

echo "Finished."
