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

PREFIX?=/opt

help: all

all:
	@echo "Usage:"
	@echo
	@echo "  make run         - Run all testcases."
	@echo "  make doc         - Generate Documentation."
	@echo "  make cleanall    - removes *pyc, documentation."
	@echo "  make static_check- runs pep8, flake8, and pylint on code."
	@echo "  make install     - copy test suite to ${PREFIX}/nvmftests

doc:
	@make -C doc/

run:
	@ln -s tests/config config
	nose2 --verbose
	@rm -fr config

static_check:
	for i in `find . -name \*.py  | grep -v __init__ | grep -v state_machine`;\
	do\
			echo "Pylint :- " ;\
			printf "%10s    " $${i};\
			pylint $${i} 2>&1  | grep "^Your code" |  awk '{print $$7}';\
			echo "--------------------------------------------";\
			echo "pep8 :- ";\
			pep8 $${i};\
			echo "flake8 :- ";\
			flake8 $${i};\
	done

cleanall: clean
	@rm -fr tests/logs tests/*fio.log loop.json logs
	@find . -name \*_fio.log | xargs rm -fr
	@make -C doc/ clean

clean:
	@rm -fr config
	@find . -name \*pyc | xargs rm -fr
	@find . -name __pycache__ | xargs rm -fr
	@find . -name \*ropeproject | xargs rm -fr

install:
	@mkdir -p ${PREFIX}/nvmftest
	@cp -r * ${PREFIX}/nvmftest

.PHONY: doc clean cleanall
