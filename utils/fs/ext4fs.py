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
""" Represents Ext4 File system.
"""
import os
import subprocess

from .filesystem import FileSystem


class Ext4FS(FileSystem):
    """
    Represents Ext4FS File System management interface.

        - Attributes :
    """
    def __init__(self, dev_path, mount_path=None):
        super(Ext4FS, self).__init__("ext4", dev_path, mount_path)

    def get_mount_path(self):
        """ Accessor for file system mountpath.
            - Args :
                - None.
            - Returns :
                - File system mountpath.
        """
        return super(Ext4FS, self).get_mount_path()

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
        """ Execute mkfs on target deivce.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        if super(Ext4FS, self).mkfs() is False:
            return False

        self.exec_cmd("mkfs.ext4 " + self.dev_path)
        print("mkfs successful!!!")
        return True

    def mount(self):
        """ Mount Target device on the mount path.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        if super(Ext4FS, self).mount() is False:
            return False
        return self.exec_cmd("mount " + self.dev_path + " " + self.mount_path)

    def is_mounted(self):
        """ Check if namespace is mounted.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        return self.exec_cmd("mountpoint -q " + self.mount_path)

    def umount(self):
        """ Unmount target device from mount path.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        if super(Ext4FS, self).umount() is False:
            return False

        ret = True
        self.exec_cmd("umount " + self.mount_path)
        try:
            os.rmdir(self.mount_path)
        except Exception as err:
            print(str(err))
            ret = False

        return ret
