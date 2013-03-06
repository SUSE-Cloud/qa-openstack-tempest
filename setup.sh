#!/bin/sh

if [ -z $TEMPESTDIR ]; then
    echo "Please define the TEMPESTDIR to your tempest directory:"
    echo "    export TEMPESTDIR=<directory of tempest directory>"
    exit -1
fi

OBJECTDIR=${TEMPESTDIR}/openstack_tempest

sed -i.bak -e "s#TEMPESTDIR#"$TEMPESTDIR"#" ./test_create_delete_server_by_upload_image.py

if [ ! -d ${TEMPESTDIR}/tempest ] || [ ! -f ${TEMPESTDIR}/etc/tempest.conf ]; then
    echo "The directory you given is not correct or you havn't configure your tempest! exit."
    exit
fi

if [ -d $OBJECTDIR ]; then
    echo "The target directory \"$OBJECTDIR\" already exist!, please remove it at first! exit."
    exit -1
else
    mkdir $OBJECTDIR
fi

cp base_test.py test_*.py $OBJECTDIR

echo "Setup finished! Now you can run tests in $OBJECTDIR"
