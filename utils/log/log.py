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
""" Represents Testcaes Logging setup.
"""
import json
import logging


class Log(object):

    """
    Represents a consoler logger setup helper for a module.
        - Attributes :
    """

    @staticmethod
    def get_logger(name, element):
        """ Returns the log level from config file.
            - Args :
                - element : NVMe Over Fabrics subsystem element.
            - Returns :
                - Valid Log level on success, None otherwise.
        """
        logger = None
        with open('config/nvmftests.json') as cfg_file:
            cfg = json.load(cfg_file)
            logger = logging.getLogger(name)
            if cfg['log'][element] == "NOTSET":
                logger.setLevel(logging.DEBUG)
            elif cfg['log'][element] == "DEBUG":
                logger.setLevel(logging.DEBUG)
            elif cfg['log'][element] == "INFO":
                logger.setLevel(logging.INFO)
            elif cfg['log'][element] == "WARNING":
                logger.setLevel(logging.WARNING)
            elif cfg['log'][element] == "ERROR":
                logger.setLevel(logging.ERROR)
            elif cfg['log'][element] == "CRITICAL":
                logger.setLevel(logging.CRITICAL)

        return logger
