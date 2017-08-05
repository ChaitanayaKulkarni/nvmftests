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
#   Author: Chaitanya Kulkarni <chaitanya.kulkarni@wdc.com>
#
""" Represents NVMe Over Fabric Host Namespace.
"""

import Queue
import time
import threading
import subprocess

from utils.const import Const
from utils.fs import Ext4FS


class NVMFNSThread(threading.Thread):
    """
    Represents a worker thread.

        - Attributes :
            - target : thread Target.
            - workq : workqueue shared between producer and worker thread.
    """
    def __init__(self, group=None, target=None, name=None,
                 args=[None], kwargs=None, verbose=None):
        """Default Thread Constructor."""
        super(NVMFNSThread, self).__init__()
        self.target = target
        self.name = name
        self.workq = args[0]
        self.q_cond_var = args[1]

    def run(self):
        """ Default Thread Function """
        while True:
            with self.q_cond_var:
                # if queue is empty wait
                if self.workq.empty():
                    self.q_cond_var.wait()

                # get the itsm from the queue if None exit
                item = self.workq.get()
                if item is None:
                    break

                ret = item['THREAD'](item)
                # On Error just shutdown the worker thread
                # complete all the remaining operations and quit
                if ret is False:
                    self.workq.put(None)
        print("Exiting workther thread " + self.name)


class NVMFHostNamespace(object):
    """
    Represents a host namespace.

        - Attributes :
            - ns_dev : block device associated with this namespace.
            - mount_path : mounted directory.
            - worker_thread : handle for io worker thread.
            - workq : workqueue shared between producer and worker thread.
            - q_cond_var : Condition variable for queue operations.
    """
    def __init__(self, ns_dev):
        self.ns_dev = ns_dev
        self.mount_path = None
        self.worker_thread = None
        self.workq = Queue.Queue()
        self.q_cond_var = threading.Condition()
        self.fs_type = None
        self.err_str = "ERROR : " + self.__class__.__name__ + " : "

    def init(self):
        """ Initialize namespace, create worker thread and
            build controller attributes.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        if self.id_ns() is False:
            return False

        # Create worker thread for this ns
        self.worker_thread = NVMFNSThread(args=[self.workq, self.q_cond_var])
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
        if ret != Const.ZERO:
            print(self.err_str + "nvme id-ctrl failed")
            return False

        return True

    def mkfs(self, fs_type):
        """ Format namespace with file system and mount on the unique
            namespace directory.
            - Args :
                  - fs_type : file system type.
            - Returns :
                  - True on success, False on failure.
        """
        if fs_type == "ext4":
            self.fs_type = Ext4FS(self.ns_dev)
            if self.fs_type.mkfs() is True and self.fs_type.mount():
                return True
        else:
            print(self.err_str + "file system is not supported")

        return False

    def unmount_cleanup(self):
        """ Unmount the namespace and cleanup the mount path.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        if self.fs_type is not None:
            return self.fs_type.umount()

        return True

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
            with self.q_cond_var:
                self.workq.put(iocfg)
                self.q_cond_var.notifyAll()
        else:
            print(self.err_str + "worker thread is not running.")
            return False

        return True

    def wait_io(self):
        """ Wait until all the items are completed from workqueue.
            - Args :
                  - None.
            - Returns :
                  - True if worker thread is alive and queue is empty,
                    False otherwise.
        """
        print("Checking for worker thread " + self.ns_dev + ".")
        if self.worker_thread.is_alive():
            print("Waiting for thread completion " + self.ns_dev + ".")
            while not self.workq.empty():
                if self.worker_thread.is_alive():
                    time.sleep(Const.ONE)
                else:
                    break
        else:
            print(self.err_str + "worker thread is not alive")
            return False
        print("# WAIT COMPLETE " + self.ns_dev + ".")
        return True

    def delete(self):
        """ Namespace clanup.
            - Args :
                  - None.
            - Returns :
                  - None.
        """
        print("##### Deleting Namespace ")
        if self.worker_thread.is_alive():
            with self.q_cond_var:
                self.workq.put(None)
                self.q_cond_var.notifyAll()

            while not self.workq.empty():
                if self.worker_thread.is_alive():
                    time.sleep(Const.ONE)
                else:
                    break

            if self.worker_thread.is_alive():
                print(self.err_str + "Worker thread is still alive ...!!!")

        self.unmount_cleanup()
