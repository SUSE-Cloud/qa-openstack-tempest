#!/bin/bash

# ensure that the tempest tools directory is in th environment path
PATH="$PATH:$(pwd)/tools"

# a helpful timestamp for when post-processing logs
log="tempest_$(date +%y%m%d_%H%M%S).log"

export NOSE_WITH_OPENSTACK=1
export TEMPEST_PY26_NOSE_COMPAT=1

# catch the stdout in a file which would otherwise be lost
time nosetests -v tempest 2>&1 | tee $log

# please note that tempest does generate an error log with timestamps,
# but this log will provide a test overview.
