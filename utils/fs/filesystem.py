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
""" Represents File System Base class.
"""
import os
import stat
import subprocess


class FileSystem(object):
    """
    Represents Ext4FS file system management interface.

        - Attributes :
            - fs_name : file system name.
            - dev_path : target device.
            - mount_path : path to mount target device.
    """
    def __init__(self, fs_name, dev_path, mount_path=None):
        self.fs_name = fs_name
        self.dev_path = dev_path
        self.mount_path = mount_path
        if self.mount_path is None:
            self.mount_path = "/mnt/" + self.dev_path.split('/')[-1]

    def exec_cmd(self, cmd):
        """ Wrapper for executing a shell command.
            - Args :
                - cmd : command to execute.
            - Returns :
                - Value of the command.
        """
        proc = None
        try:
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        except Exception as err:
            print(str(err) + ".")
            return False

        return True if proc.wait() == 0 else False

    def mkfs(self):
        """ Check preconditions for the mkfs operation.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        if not os.path.exists(self.dev_path):
            print("ERROR : device path %s is not present.", self.dev_path)
            return False

        if not stat.S_ISBLK(os.stat(self.dev_path).st_mode):
            print("ERRO : block device expected for mkfs.")
            return False
        if self.is_mounted() is True:
            print("ERROR : device is already mounted.")
            return False

        return True

    def mount(self):
        """ Check preconditions for the mount operation.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        if not os.path.exists(self.mount_path):
            try:
                os.makedirs(self.mount_path)
            except Exception as err:
                print(str(err))
                return False

        return True

    def get_mount_path(self):
        """ Accessor for file system mountpath.
            - Args :
                  - None.
            - Returns :
                  - File system mountpath.
        """
        return self.mount_path

    def umount(self):
        """ Check preconditions for the umount operation.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        if not self.is_mounted():
            print("ERROR : fs is not mounted")
            return False

        return True

    def is_mounted(self):
        """ Check if namespace is mounted.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        return self.exec_cmd("mountpoint -q " + self.mount_path)
