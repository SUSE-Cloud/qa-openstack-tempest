#!/bin/bash

log="tempest_$(date +%y%m%d_%H%M%S).log"
time nosetests -v tempest 2>&1 | tee $log
