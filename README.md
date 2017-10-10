nvmftests
=========


1. Introduction
---------------

    This contains NVMe Over Fabrics unit test framework. The purpose of this
    framework is to provide a platform to create different scenarios and test
    specific functionality for NVMe Over Fabrics Subsystem (NVMeOF).

2. Overview
-----------

    The main objective of this framework is to have a platform in place which
    can provide :-
        1. Classes and methods for each component in the NVMeOF subsystem.
        2. Ability to build NVMeOF subsystem based on the configuration file.
        3. Ability to issue sequential and parallel commands to the different
           namespaces and controllers from the host and target side.

    All the testcases are written in python3 and nose2 format.

3. Class hierarchy, design Considerations and directory structure
-----------------------------------------------------------------

    This framework follows a simple class hierarchy. Each test is a
    direct subclass or indirect subclass of NVMeOFTest. To write a new testcase
    one can copy an existing template test_nvmf_target_template.py or
    test_nvmf_host_template.py and start adding new testcase specific
    functionality.

    3.1. Core Classes :- (path $NVMFTESTSHOME/nvmf/)
       Target Classes :- (path $NVMFTESTSHOME/nvmf/target)
           NVMeOFTarget :- Represents Target.
           NVMeOFTargetSubsystem :- Represents a Target Subsystem.
           NVMeOFTargetNamespace :- Represents a Target Namespace.
           NVMeOFTargetPort :- Represents a Target Port.
       Host Classes :- (path $NVMFTESTSHOME/nvmf/host)
           NVMeOFHost :- Represents Host.
           NVMeOFHostController :- Represents a Host Controller.
           NVMeOFHostNamespace :- Represents a Host Namespace.

       We divide host and target side components into two different class
       hierarchies. On the host side, we have a controller represented as a
       character device and each namespace as a block device. In order to
       add any new functionality to the framework please modify core classes
       for each component and propagate new interfaces to the top
       level (in host.py/target.py). On the target side, we have subsystem(s),
       namespace(s), and port(s) which are configured using configfs.
       For detailed class hierarchy please look into documentation.
    3.2. Testcase class:-
        NVMeOFTest :- Base class for each testcase, contains common functions.
                      Each testcase is direct or indirect subclass of
                      NVMeOFTest. Testcase class consumes the host and target
                      classes mentioned in the 3.1 to build the
                      NVMeOF subsystems.
    3.3 Directory Structure
        Following is the quick overview of the directory structure :-
        .
        |-- doc                 :- documentation.
        |   |-- Documentation   :- class documentation.
        |   |-- sequence-diag   :- sequence diagram.
        |-- nvmf                :- NVMF core test framework files.
        |   |-- host            :- NVMF host core files.
        |   |-- target          :- NVMF target core files.
        |-- tests               :- test cases.
        |   |-- config          :- test configuration JSON files.
        |-- utils               :- utility classes.
            |-- const           :- constant(s) definitions.
            |-- diskio          :- diskio related wrappers.
            |-- fs              :- fs related wrappers.
            |-- misc            :- miscellaneous files.
            |-- shell           :- shell command related wrappers.
            |-- log             :- module logger helpers.


4. Adding new testcases
-----------------------

    4.1. Please refer to host or target template testcase.
    4.2. Copy the template file with your testcase name.
    4.3. Update the class name with testcase name, this has to be unique.
    4.4. Update the test case function name.
    4.5. If necessary update the core files and add new functionality.
    4.6. Add testcase main function to determine success or failure.
    4.7. Update setUp() and tearDown() to add pre and post functionality.
    4.8. Once testcase is ready make sure :-
         4.8.1. Run pep8, flake8, pylint and fix errors/warnings.
                -Example "$ make static_check" will run pep8, flake8, and
                pylint on all the python files in current directory.
         4.8.2. Execute make doc to generate the documentation.
                -Example "$ make doc" will create and update existing
                 documentation.

5. Running testcases with framework
-----------------------------------

    Here are some examples of running testcases with nose2 :-
        5.1. Running single testcase with nose2 :-
            from $NVMFTESTSHOME/tests
            # nose2 --verbose test_nvmf_create_target
            # nose2 --verbose test_nvmf_create_host

        5.2. Running all the testcases :-
            from $NVMFTESTSHOME/tests
            # nose2 --verbose

        5.3 Running all the testcases from makefile :-
            from #NVMFTESTSHOME
            # make run

    Some notes on execution:-
        In the current implementation, it uses file backed loop or nvme-pci
        block device on the target side. For some testcase execution,
        a new file is created and linked with loop device. It expects that
        "mount_path" in the nvmftests.json has enough space available to store
        backend files which are used for target namespaces. Please edit the
        target subsystems and namespace configuration, size of the loop device
        backed file on the target side in the
        $NVMFTESTSHOME/tests/config/nvmftests.json according to your need.

        For host and target setup, you may have to configure timeout (sleep())
        values in the code to make sure previous steps are completed
        successfully and resources are online before executing next the steps.
        We are planning to make these sleep() calls configurable in the future
        release.

6. Logging
----------

    For each testcase, it will create a separate log directory with the test
    name under logs/. This directory will be used for temporary files and
    storing execution logs of each testcase. Current implementation stores
    stdout and stderr for each testcase under log directory, e.g.:-
        logs/
        |-- TestNVMFCreateHost
        |   |-- TestNVMFCreateHost
        |       |-- stderr.log
        |       |-- stdout.log
        |-- TestNVMFCreateTarget
        |   |── TestNVMFCreateTarget
        |       |-- stderr.log
        |       |-- stdout.log
        |-- TestNVMFCtrlRescan
        |   |-- TestNVMFCtrlRescan
                .
                .
                .

7. Test configuration
---------------------

    There are two types of config files used by the framework :-
    1. nvmftests.json :- ($NVMFTESTSHOME/tests/config/nvmftests.json) file
       contains the information about various testcase parameters.
    2. loop.json :- This file is auto-generated by the test framework
       for the target configuration based on the parameters set in the
       nvmftests.json.

9. Dependencies
---------------

    9.1. Python( >= 3.0)
    9.2. nose(http://nose.readthedocs.io
    9.3. nose2(Installation guide http://nose2.readthedocs.io/)
    9.4. pep8(https://pypi.python.org/pypi/setuptools-pep8)
    9.5. flake8(https://pypi.python.org/pypi/flake8)
    9.6. pylint(https://www.pylint.org/)
    9.7. Epydoc(http://epydoc.sourceforge.net/)
    9.8. nvme-cli(https://github.com/linux-nvme/nvme-cli.git)

    Python package management system pip can be used to install most of the
    listed packages(https://pip.pypa.io/en/stable/installing/) :-

    $ pip install nose nose2 natsort pep8 flake8 pylint epydoc
