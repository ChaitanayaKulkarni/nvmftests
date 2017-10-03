###############################################################################
#
#    Makefile : Allows user to run testcases, generate documentation, and
#               perform static code analysis.
#
###############################################################################

help: all

all:
	@echo "Usage:"
	@echo
	@echo "  make run         - Run all testcases."
	@echo "  make doc         - Generate Documentation."
	@echo "  make cleanall    - removes *pyc, documentation."
	@echo "  make static_check- runs pep8, flake8, and pylint on code."

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
			pep8 $${i};\
			echo "pep8 :- ";\
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

.PHONY: doc clean cleanall
