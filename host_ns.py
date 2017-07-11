
# Copyright (c) 2016-2017 Western Digital Corporation or its affiliates.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.
#
#   Author: Chaitanya Kulkarni <chaitanya.kulkarni@hgst.com>
#
""" Represents NVMe Over Fabric Host Namespace.
"""

import os
import Queue
import threading
import subprocess

from utils.fs import Ext4FS

class NVMeOFNSThread(threading.Thread):
    """
    Represents a worker thread.

        - Attributes :
            - target : thread Target.
            - workq : workqueue shared between producer and worker thread.
    """
    def __init__(self, group=None, target=None, name=None,
                 args=[None], kwargs=None, verbose=None):
        """Default Thread Constructor."""
        super(NVMeOFNSThread, self).__init__()
        self.target = target
        self.name = name
        self.workq = args[0]

    def run(self):
        """ Default Thread Function """
        while True:
            if not self.workq.empty():
                item = self.workq.get()
                if item is None:
                    break
                ret = item['THREAD'](item)
                self.workq.task_done()
                # On Error just shutdown the worker thread.
                # Need to implement qid based work queue implementation.
                if ret is False:
                    self.workq.put(None)


class NVMeOFHostNamespace(object):
    """
    Represents a host namespace.

        - Attributes :
            - ns_dev : block device associated with this namespace.
            - lbaf_cnt : logical block format count.
            - ns_dict : namespace attributes.
            - lbaf : dictionary for logical block format.
            - ms : dictionary to store medata size information.
            - lbads : dictionary to store LBA Data Size.
            - rp : dictionary to store relative performance.
            - mount_path : mounted directory.
            - worker_thread : handle for io worker thread.
            - workq : workqueue shared between producer and worker thread.
    """
    def __init__(self, ns_dev):
        self.ns_dev = ns_dev
        self.lbaf_cnt = 0
        self.ns_dict = {}
        self.lbaf = {}
        self.ms = {}
        self.lbads = {}
        self.rp = {}
        self.mount_path = None
        self.worker_thread = None
        self.workq = Queue.Queue()
        self.ext4fs = Ext4FS(self.ns_dev)
        self.err_str = "ERROR : " + self.__class__.__name__ + " : "

    def init(self):
        """ Initialize nameapce, create worker thread and
            build controller attributes.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        if self.id_ns() is False:
            return False

        # Create IO worker thread for this ns
        self.worker_thread = NVMeOFNSThread(args=[self.workq])
        self.worker_thread.setDaemon(True)
        self.worker_thread.start()
        return True

    def id_ns(self):
        """ Wrapper for id-ns command.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        id_ctrl_cmd = "nvme id-ns " + self.ns_dev
        proc = subprocess.Popen(id_ctrl_cmd,
                                shell=True,
                                stdout=subprocess.PIPE)
        ret = proc.wait()
        if ret != 0:
            print(self.err_str + "nvme id-ctrl failed")
            return False

        i = 0
        for line in proc.stdout:
            if line.startswith('subnqn') or \
               line.startswith('NVME Identify Nameapce'):
                continue
            if line.startswith('lbaf'):
                self.lbaf[i] = line.split(':')[0].split('  ')[1]
                self.ms[i] = line.split(':')[2].split('  ')[0]
                self.lbads[i] = line.split(':')[3].split(' ')[0]
                self.rp[i] = line.split(':')[4].split(' ')[0]
                i += 1
                continue

            key, value = line.split(':')
            self.ns_dict[key.strip()] = value.strip()
        return True

    def get_value(self, k):
        """ Access nvme namespace attribute's value based on the key.
            - Args :
                  - k : represents namespace's attribute.
            - Returns :
                  - None.
        """
        return self.ns_dict[k]

    def mkfs_seq(self):
        """ Format namespace with file system and mount on the unique
            namespace directory.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        if self.ext4fs.mkfs() is True and self.ext4fs.mount():
            return True

        return False 

    def unmount_cleanup(self):
        """ Unmount the namespace and cleanup the mount path.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        return self.ext4fs.umount()

    def start_io(self, iocfg):
        """ Add new work item to workqueue. Triggers wake up in worker thread.
            - Args :
                  - IO Configuration passed to worker thread.
            - Returns :
                  - True on success, False on failure.
        """
        if iocfg['IODIR'] == "read":
            iocfg['IF'] = self.ns_dev
        elif iocfg['IODIR'] == "write":
            iocfg['OF'] = self.ns_dev
        else:
            print(self.err_str + "io config " + iocfg + " not supported.")
            return False

        if self.worker_thread.is_alive():
            self.workq.put(iocfg)
        else:
            print(self.err_str + "worker thread is not running.")
            return False

        return True

    def wait_io(self):
        """ Wait until all the items are completed from workqueue.
            - Args :
                  - None.
            - Returns :
                  - None.
        """
        print("Checking for worker thread " + self.ns_dev + ".")
        if self.worker_thread.is_alive():
            print("Waiting for thread completion " + self.ns_dev + ".")
            self.workq.join()
        print("# WAIT COMPLETE " + self.ns_dev + ".")

    def delete(self):
        """ Namespace clanup.
            - Args :
                  - None.
            - Returns :
                  - None.
        """
        print("##### Deleting Namespace ")
        self.workq.put(None)

        self.unmount_cleanup()
