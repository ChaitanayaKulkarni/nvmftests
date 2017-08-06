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
""" Represents FIO wrapper
"""

import subprocess


class FIO(object):

    """
    Represents fio command wrapper.
    """

    @staticmethod
    def run_fio(iocfg):
        """ Executes fio command based on the config argument.
            - Args :
                  - IO Configuration for fio command.
            - Returns :
                  - True on success, False on failure.
        """
        cmd = "fio "
        cmd += " --group_reporting=" + iocfg['group_reporting']
        cmd += " --rw=" + iocfg['rw']
        cmd += " --bs=" + iocfg['bs']
        cmd += " --numjobs=" + iocfg['numjobs']
        cmd += " --iodepth=" + iocfg['iodepth']
        cmd += " --runtime=" + iocfg['runtime']
        cmd += " --loops=" + iocfg['loop']
        cmd += " --ioengine=" + iocfg['ioengine']
        cmd += " --direct=" + iocfg['direct']
        cmd += " --invalidate=" + iocfg['invalidate']
        cmd += " --randrepeat=" + iocfg['randrepeat']
        cmd += " --time_based "
        cmd += " --norandommap"
        cmd += " --exitall"
        cmd += " --size=" + iocfg['size']
        cmd += " --filename=" + iocfg['filename']
        cmd += " --name=" + iocfg['name']

        print(cmd)
        ret = True
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        rc = proc.wait()
        if rc != iocfg['RC']:
            print(".")
            ret = False
        return ret


iocfg = {}

iocfg['group_reporting'] = "1"
iocfg['rw'] = "randread"
iocfg['bs'] = "4k"
iocfg['numjobs'] = "4"
iocfg['iodepth'] = "8"
iocfg['runtime'] = "10"
iocfg['loop'] = "1"
iocfg['ioengine'] = "libaio"
iocfg['direct'] = "1"
iocfg['invalidate'] = "1"
iocfg['randrepeat'] = "1"
iocfg['size'] = "100M"
iocfg['filename'] = "/dev/nvme1n1"
iocfg['name'] = "test1"
iocfg['RC'] = "0"
FIO.run_fio(iocfg)
