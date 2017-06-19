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
""" Represents NVMe Over Fabric Target Namespace.
"""

import os
import shutil
import subprocess


class NVMeOFTargetNamespace(object):
    """
    Represents a target namespace.

        - Attributes :
            - ns_attr : namespace attributes.
            - cfgfs : configfs path
            - nqn : subsystem nqn
            - ns_id : namespace identifier.
            - ns_path : namespace path in configfs path.
            - ns_attr : namespace attributes.
    """
    def __init__(self, cfgfs, nqn, ns_id, **ns_attr):
        self.ns_attr = {}
        self.cfgfs = cfgfs
        self.nqn = nqn
        self.ns_id = ns_id
        self.ns_path = (self.cfgfs + "/nvmet/subsystems/" +
                        nqn + "/namespaces/" + str(ns_id) + "/")
        self.ns_attr['device_nguid'] = ns_attr['device_nguid']
        self.ns_attr['device_path'] = ns_attr['device_path']
        self.ns_attr['enable'] = ns_attr['enable']
        self.err_str = "ERROR : " + self.__class__.__name__ + " : "

    def init_ns(self):
        """ Create and initialize namespace.
            - Args :
                - None.
            - Returns :
                  - True on success, False on failure.
        """
        print "####Creating ns " + self.ns_path
        try:
            os.makedirs(self.ns_path)
        except Exception, err:
            print self.err_str + str(err) + "."
            return False

        cmd = "echo -n " + self.ns_attr['device_path'] + " > " + \
              self.ns_path + "/device_path"
        ret = self.exec_cmd(cmd)
        if ret is False:
            print self.err_str + "failed to configure device path."
            return False

        if self.ns_attr['enable'] == '1':
            ret = self.ns_enable()
            if ret is False:
                print self.err_str + "enable ns " + self.ns_path + " failed."
                return False

        print "NS " + self.ns_path + " enabled."
        return True

    def exec_cmd(self, cmd):
        """ Wrapper for executing a shell command.
            - Args :
                - cmd : command to execute.
            - Returns :
                - True if cmd returns 0, False otherwise.
        """
        proc = None
        try:
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        except Exception, err:
            print self.err_str + str(err) + "."
            return False

        return True if proc.wait() == 0 else False

    def ns_disable(self):
        """ Disable Namespace.
            - Args :
                - None.
            - Returns :
                - True on success, False on failure.
        """
        self.ns_attr['enable'] = "0"
        return self.exec_cmd("echo 0 > " + self.ns_path + "/enable")

    def ns_enable(self):
        """ Enable Namespace.
            - Args :
                - None.
            - Returns :
                  - True on success, False on failure.
        """
        self.ns_attr['enable'] = "1"
        return self.exec_cmd("echo 1 > " + self.ns_path + "/enable")

    def del_ns(self):
        """ Delete This Namespace.
            - Args :
                - None.
            - Returns :
                  - True on success, False on failure.
        """
        print "Removing NS " + self.ns_path
        ret = os.path.exists(self.ns_path)
        if ret is True:
            # TODO : improve cleanup funcitonality.
            shutil.rmtree(self.ns_path, ignore_errors=True)
        else:
            print self.err_str + "path " + self.ns_path + " doesn't exists."
        return ret
