#!/bin/bash
# Copyright (c) 2015 PMC and/or its affiliates. All Rights Reserved.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it would be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# Author: stephen.bates@pmcs.com <stephen.bates@pmcs.com>

CONFIGFS=${CONFIGFS-/sys/kernel/config}
CTRL_SYSFS=/sys/class/nvme

nvmf_unload_driver()
{
	driver=$1
	rmmod $driver
}

nvmf_load_driver()
{
	driver=$1
	modprobe $driver
}

nvmf_delete_ctrl()
{
    echo 1 > $CTRL_SYSFS/$1/delete_controller
}

nvmf_reset_ctrl()
{
    echo 1 > $CTRL_SYSFS/$1/reset_controller
}

nvmf_namespace()
{
    local nqn=$1
    local nsid=$2
    local dev=$3

    mkdir -p "$CONFIGFS/nvmet/subsystems/$nqn/namespaces/$nsid"
    echo -n $dev > "$CONFIGFS/nvmet/subsystems/$nqn/namespaces/$nsid/device_path"
    echo 1 > "$CONFIGFS/nvmet/subsystems/$nqn/namespaces/$nsid/enable"
}

nvmf_target()
{
    modprobe nvmet

    sleep 1 # Need this to avoid race

    mkdir -p "$CONFIGFS/nvmet/subsystems/$1"
    echo 1 > "$CONFIGFS/nvmet/subsystems/$1/attr_allow_any_host"
}

nvmf_loop_target()
{
    modprobe nvme-loop
    nvmf_target $*

    mkdir -p "$CONFIGFS/nvmet/ports/1"
    echo -n "loop" > "$CONFIGFS/nvmet/ports/1/addr_trtype"
    ln -s "$CONFIGFS/nvmet/subsystems/$1" "$CONFIGFS/nvmet/ports/1/subsystems"
}

nvmf_rdma_target()
{
    modprobe nvmet-rdma
    nvmf_target $*

    traddr=${2:-0.0.0.0}
    mkdir -p "$CONFIGFS/nvmet/ports/1"
    echo $traddr > $CONFIGFS/nvmet/ports/1/addr_traddr
    echo 1023 > $CONFIGFS/nvmet/ports/1/addr_trsvcid
    echo -n "ipv4" > $CONFIGFS/nvmet/ports/1/addr_adrfam
    echo -n "rdma" > $CONFIGFS/nvmet/ports/1/addr_trtype

    ln -s "$CONFIGFS/nvmet/subsystems/$1" "$CONFIGFS/nvmet/ports/1/subsystems"
}

_nvmf_host()
{
    modprobe nvme-fabrics
    echo "$2,nqn=$1" > /dev/nvme-fabrics

    local DEV_PATH=$(grep -ls $1 /sys/class/nvme-fabrics/ctl/*/subsysnqn)
    echo $(basename $(dirname $DEV_PATH))
}

nvmf_loop_host()
{
    _nvmf_host $1 "transport=loop"
}

nvmf_rdma_host()
{
    modprobe nvme-rdma
    _nvmf_host $1 "transport=rdma,traddr=$2,trsvcid=$3"
}

  # Note we always want nvme_cleanup to try all the rmmods so we wrap
  # it in a set +/-e.

nvmf_cleanup_host()
{
    SAVED_OPTIONS=$(set +o)
    set +e

    local DEV_PATH=$(grep -ls $1 /sys/class/nvme-fabrics/ctl/*/subsysnqn)

    if [ -e "$DEV_PATH" ]; then
        DEV_PATH=$(dirname $DEV_PATH)
        echo > $DEV_PATH/delete_controller
    fi

    modprobe -r nvme-rdma

    eval "$SAVED_OPTIONS"
}

nvmf_cleanup_target()
{
    SAVED_OPTIONS=$(set +o)
    set +e

    if [ -d $CONFIGFS/nvmet/ports/1 ]; then
	rm -f $CONFIGFS/nvmet/ports/1/subsystems/*
	rmdir $CONFIGFS/nvmet/ports/1
    fi
    for i in $CONFIGFS/nvmet/subsystems/$1/namespaces/*; do
        rmdir $i
    done
    rmdir $CONFIGFS/nvmet/subsystems/$1
    modprobe -r nvmet-rdma
    modprobe -r nvme-loop
    modprobe -r nvmet

    eval "$SAVED_OPTIONS"
}

nvmf_cleanup()
{
    nvmf_cleanup_host $1

    if [ "${TARGET_HOST}" != "" ]; then
        nvmf_remote_cmd ${TARGET_HOST} nvmf_cleanup_target $1
    else
        nvmf_cleanup_target $1
    fi
}

nvmf_check_configfs_mount()
{
      # If mountpoint exists use it to ensure that configfs is already
      # mounted.

    if [ $(which mountpoint) ]
    then
        if !(mountpoint -q ${CONFIGFS})
        then
	    echo nvmf: configfs is not mounted.
	    exit -1
        fi
    else
        echo nvmf: Warning: automount not found - skipping configfs check.
    fi
}

nvmf_check_target_device()
{
      # Set up the target block device. Note that in-reality any block
      # device can be supported here. If the device is the null_blk device
      # then we create it here if it does not already exist.

    if [[ "$1" == "/dev/nullb"* ]]
    then
        if [ ! -b "$1" ]
        then
            modprobe null_blk
        fi
    fi

    if [ ! -b "$1" ]
    then
        echo nvmf: Error: Could not find target device.
        exit -1
    fi
}

nvmf_setup_dd_args()
{
     local COUNT=$1
     local BS=$2
     local DIRECT=$3
     local SYNC=$4

    # Setup the dd iflag and oflag based on user input.

     if [ "${DIRECT}" == TRUE ]
     then
         if [ "${SYNC}" == TRUE ]
         then
	     FLAGS="direct,sync"
         else
	     FLAGS="direct"
         fi
     else
         if [ "${SYNC}" == TRUE ]
         then
	     FLAGS="sync"
	 else
	     FLAGS="none"
         fi
     fi

     echo "$FLAGS bs=${BS} count=${COUNT} ${IFLAG}"
}

nvmf_remote_cmd()
{
    local HOST=$1
    shift

    ssh ${HOST} bash <<-EOF
        $(set +o)
        $(cat ./nvmf_lib.sh)
        $@
	EOF

}

nvmf_run_fio_bg()
{
    bs=${1:-"4k"}
    pattern=${2:-"randread"}
    th=${3:-"1"}
    iod=${4:-"32"}
    time=${5:-"30"}
    devs=${*:6}

    fio_cmd="fio --group_reporting --rw=$pattern --bs=$bs --numjobs=$th --iodepth=$iod --runtime=$time
    --time_based --loops=1 --ioengine=libaio  --direct=1 --invalidate=1 --randrepeat=1 --norandommap
    --exitall --size=100M"

    i=0
    for dev in $devs
    do
        fio_cmd="$fio_cmd --name task_$i --filename=$dev"
	let "i+=1"
    done

    $fio_cmd > /dev/null 2>&1 &
}

nvmf_run_dd()
{
    DEV=$1
    FLAGS=$2
    shift 2

    if [ "${FLAGS}" != "none" ]; then
        IFLAGS="iflag=$FLAGS"
	OFLAGS="oflag=$FLAGS"
    fi

    echo -n "  READ:  "
    dd if=$DEV of=/dev/null $IFLAGS $* 2>&1 | tail -n 1
    echo -n "  WRITE: "
    dd if=/dev/zero of=$DEV $OFLAGS $* 2>&1 | tail -n 1
}

nvmf_check_cleanup_only()
{
      # If requested just run the cleanup function. Useful if a previous
      # run has left the system in a undefined state.

    if [ "${CLEANUP_ONLY}" == TRUE ]
    then
        echo nvmf: Just performing cleanup.
        nvmf_cleanup $1 2> /dev/null
        exit -1
    fi
}

nvmf_trap_exit()
{
    if [ "${CLEANUP_SKIP}" == FALSE ]
    then
        finish()
        {
            sync
            echo
	    echo "Cleaning Up"
            nvmf_cleanup ${NAME}
        }

        trap finish EXIT
    fi
}
