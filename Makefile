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
	@epydoc -v --output=Documentation *.py

run:
	nose2 ${NOSE2_OPTIONS}

static_check:
	@for i in `ls *.py`; \
	do \
		echo "Pylint :- " ; \
		printf "%10s    " $${i}; \
		pylint $${i} 2>&1  | grep "^Your code" |  awk '{print $$7}';\
		echo "--------------------------------------------";\
		pep8 $${i}; \
		echo "pep8 :- "; \
		echo "flake8 :- "; \
		flake8 $${i}; \
	done

cleanall: clean
	@rm -fr Documentation logs/*

clean:
	@find . -name \*pyc | xargs rm -fr
	@find . -name __pycache__ | xargs rm -fr
