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
""" Represents Shell Command execution.
"""
import subprocess

class Const:

    """
    Represents a host.
        - Attributes :
            All constants for testcases
    """

    XXX = "XXX"
    ONE_KB = 1024
    ONE_MB = ONE_KB * ONE_KB
    ONE_GB = ONE_MB * ONE_KB

    KB = "KB"
    MB = "MB"
    GB = "GB"

    EXT4 = "ext4"

    CTRL_BLK_FILE_NAME = 2
    SMART_LOG_VALUE = 1
    ALLOW_HOST_VALUE = 0
