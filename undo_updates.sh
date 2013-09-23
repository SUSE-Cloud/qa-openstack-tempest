#!/bin/bash

# get a list of backed-up files
bk_list=$(find | grep '^.*\.py\.bk$')

# remove all the substitiutes and replace them with the originals
for f in $bk_list; do

  sub=$(echo $f | sed 's/.py.bk/.py/g')
  rm $sub
  mv $f $sub
done

# perform a check
find ./tempest/ | grep '^.*\.py\.bk$'

if [ $? -eq 0 ]; then
  echo "WARNING: there are still backup files."
fi

grep -ir '# SUSE Cloud 2.0 modifications (below)' ./tempest

if [ $? -eq 0 ]; then
  echo "WARNING: not all the SUSE modifications have been removed."
fi

echo "Finished!"
