#!/bin/bash

for i in `ls *.py`; 
	do 
		echo "_____________________Running ${i}_____________________"; 
		TESTCASE_NAME=`echo ${i} | cut -f 1 -d '.'`; 
		nose2 --verbose ${TESTCASE_NAME}
done
