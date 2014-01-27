#!/bin/bash

# Hard code for submitting data to qadb
rbase="/tmp";
rhost="147.2.207.113"
ruser="rd-qa"
sdkurl="http://dist.ext.suse.de/ibs/QA:/Head/SUSE_SLE-11-SP3_GA"

# add access permission to qadb server

if [ -n "$WORKDIR" ]; then
	cd $WORKDIR
	if [ $? -ne 0 ]; then
		echo "Can not enter dirctory $WORKDIR, exit."
		exit
	fi
fi

# detect if qa_lib_keys package installed
keyrpm=$(rpm -qa | grep qa_lib_keys)

if [ -z $keyrpm ]; then
	zypper --no-gpg-checks ar $sdkurl sdk
	zypper --no-gpg-checks ref -r sdk
	zypper in -y qa_lib_keys

	if [ $? -ne 0 ]; then
		echo "Install qa_lib_keys package failed, exit."
		exit
	fi
fi

# Create the directory for storing the submitted logs
if [ ! -d submitlogs ]; then
	mkdir submitlogs
fi

# Create the direcory for storing logs for user to get the logs easily.
if [ ! -d logs ]; then
	mkdir logs
fi

if [ -d cloud ]; then
	echo "move old cloud to oldlogs dir"
	mv cloud submitlogs/cloud-$(date +%Y-%m-%d-%H-%M-%S)
fi

echo "Collect data for cloud ..."
filelist=`find . -maxdepth 1 -regextype "posix-egrep" -regex ".*tempest_[0-9]{6}_[0-9]{6}.log" -type f`
if [ ! -n "$filelist" ]; then
	echo "Can not find any valid tempest log file to submit, exit."
	exit
else
	echo "find all of the files are: $filelist"
	echo "Will collect data and handle all of the file ..."
fi

for file in $filelist
do
	echo "find file: $file, will collect data and submit it"

	# Save the logs
	cp $file logs/

	testsuite=$(basename $file ".log")

	mkdir -p cloud/$testsuite

	if [ -f tempest.log ]; then
		cp tempest.log cloud/$testsuite
	else
		echo "Can not find the tempest log file: tempest.log"
	fi

	if [ -f etc/tempest.conf ]; then
		cp etc/tempest.conf cloud/$testsuite
	else
		echo "Can not find the tempest config file: etc/tempest.conf"
	fi

	rpm -qa --qf "%{NAME} %{VERSION}-%{RELEASE}\n" | sort > cloud/$testsuite/rpmlist
	/usr/sbin/hwinfo --all > cloud/$testsuite/hwinfo

	kernel_rpm=`rpm -qf /boot/System.map-$(uname -r)`
	if [ ! -z "$kernel_rpm" ]; then
		rpm -qi "$kernel_rpm" > cloud/$testsuite/kernel
	else
		uname -r > cloud/$testsuite/kernel
	fi

	mv $file cloud/$testsuite
done

host=$(hostname)
ctime=$(date +%Y-%m-%d-%H-%M-%S)
tarfile="tempest_${host}_$ctime.tar.gz"
tar zcvf /tmp/$tarfile cloud
mv cloud submitlogs/cloud-$(date +%Y-%m-%d-%H-%M-%S)

echo "scp data to qadb server ..."
# scp the target file to qadb server
scp /tmp/$tarfile $ruser@$rhost:/$rbase

if [ $? -ne 0 ]; then
	echo "Can not scp data to qadb server, exit."
	exit
fi

echo "Get information of your system ..."
pv=`cat /etc/SuSE-release | grep "VERSION" | awk -F= '{print $2}' | sed 's/\s//g'`
pr=`cat /etc/SuSE-release | grep "PATCHLEVEL" | awk -F= '{print $2}' | sed 's/\s//g'`

product=SLES-$pv-SP${pr}-GA
arch=$(uname -i)
kernel=$(uname -r)

echo 'Submit data to qadb...'
echo "ssh $ruser@$rhost /usr/share/qa/tools/qa_db_report.pl -c \"SUSE cloud tempest run on $ctime\" -a $arch -m $host -p $product -k $kernel -f /tmp/$tarfile -L -R"

ssh $ruser@$rhost "/usr/share/qa/tools/qa_db_report.pl -c \"SUSE cloud tempest run on $ctime\" -a $arch -m $host -p $product -k $kernel -f /tmp/$tarfile -L -R"

echo 'Data submit finished!'

