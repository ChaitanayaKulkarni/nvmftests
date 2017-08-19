###############################################################################
#
#    Makefile : Allows user to run testcases, generate documentation, and
#               perform static code analysis.
#
###############################################################################

NOSE2_OPTIONS="--verbose"

help: all

all:
	@echo "Usage:"
	@echo
	@echo "  make run         - Run all testcases."
	@echo "  make doc         - Generate Documentation."
	@echo "  make cleanall    - removes *pyc, documentation."
	@echo "  make static_check- runs pep8, flake8, pylint on code."

doc:
	make -C doc/

run:
	nose2 ${NOSE2_OPTIONS}

cleanall: clean
	@rm -fr tests/logs/* tests/*fio.log
	@make -C doc/ clean
 
clean:
	@find . -name \*pyc | xargs rm -fr
	@find . -name __pycache__ | xargs rm -fr
	@find . -name \*ropeproject | xargs rm -fr

.PHONY: doc clean cleanall
