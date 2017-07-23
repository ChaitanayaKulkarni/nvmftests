nvmftests
=========


1. Introduction
---------------

    This contains NVMe Over Fabrics unit test framework. The purpose of this
    framework is to provide a platform to create different scenarios and test
    specific functionality for NVMe Over Fabrics Subsystem.

2. Overview
-----------

    The main objective of this framework is to have a platform in place which
    can provide :-
        1. Classes and methods for each component in the NVMeOF subsystem.
        2. Ability to build NVMeOF subsystem based on the configuration file.
        3. Ability to issue sequential and parallel commands to the different
           namespaces and controllers from the host side.

    All the testcases are written in python nose2 format. This framework
    follows a simple class hierarchy. Each test is a direct subclass or indirect
    subclass of NVMeOFTest. To write a new testcase one can copy an existing
    template test_nvmf_target_template.py or test_nvmf_host_template.py and
    start adding new testcase specific functionality.

3. Class hierarchy and Design Considerations
--------------------------------------------

    3.1. Core Classes :-
       Target Classes :-
           NVMeOFTarget :- Represents Target.
           NVMeOFTargetSubsystem :- Represents a Target Subsystem.
           NVMeOFTargetNamespace :- Represents a Target Namespace.
           NVMeOFTargetPort :- Represents a Target Port.
       Host Classes
           NVMeOFHost :- Represents Host.
           NVMeOFHostController :- Represents a Host Controller.
           NVMeOFHostNamespace :- Represents a Host Namespace.

       We divide host and target side components into two different class
       hierarchies. On the host side, we have a controller represented as a
       character device and each namespace as a block device. In order to
       add any new functionality to the framework please modify core classes
       for each component and propagate new interfaces to the top
       level (in host.py/target.py). On the target side, we have subsystem(s),
       namespace(s), and port(s) which is mainly configured using configfs.
       For detailed class hierarchy please look into Documentation/index.html.
    3.2. Testcase class:-
        NVMeOFTest :- Base class for each testcase, contains common functions.

4. Adding new testcases
-----------------------

    4.1. Please refer host or target template testcase.
    4.2. Copy the template file with your testcase name.
    4.3. Update the class name with testcase name.
    4.4. Update the test case function name.
    4.5. If necessary update the core files and add new functionality.
    4.6. Add testcase main function to determine success or failure.
    4.7. Update setUp() and tearDown() to add pre and post functionality.
    4.8. Once testcase is ready make sure :-
         4.8.1. Run pep8, flake8, pylint and fix errors/warnings.
                -Example "$ make static_check" will run pep8, flake8 and pylint
                 on all the python files in current directory.
         4.8.2. Execute make doc to generate the documentation.
                -Example "$ make doc" will create and update existing
                 documentation.

5. Running testcases with framework
-----------------------------------

    Here are some examples of running testcases with nose2 :-
        5.1. Running single testcase with nose2 :-
            # nose2 --verbose test_nvmf_create_target
            # nose2 --verbose test_nvmf_create_host

        5.2. Running all the testcases :-
            # nose2 --verbose

    Some notes on execution:-
        In the current implementation, it uses file backed loop device on the
        target side. For each testcase execution, new file is created and linked
        with loop device. It expects that "/mnt/" has enough space available to
        store backend files which are used for target namespaces. Please edit
        the target subsystems and namespace configuration in loop.json and
        size of the loop device on the target side in the nvmf_test.py
        according to your need.

        For host and target setup you may have to configure timeout (sleep())
        values in the code to make sure previous steps are completed
        successfully and resources are online before executing next the steps.

6. Logging
----------

    For each testcase, it will create a separate log directory with the test
    name under logs/. This directory will be used for temporary files and
    storing execution logs of each testcase. Current implementation stores
    stdout and stderr for each testcase under log directory, e.g.:-
        logs/
        |-- TestNVMeOFParallelFabric
        |       |-- stderr.log
        |       |-- stdout.log
        |-- TestNVMeOFRandomFabric
        |       |-- stderr.log
        |       |-- stdout.log
        |--- TestNVMeOFSeqFabric
                |-- stderr.log
                |-- stdout.log
                .
                .
                .

7. Test configuration
---------------------

	Right now we use two json config file loop.json and nvmftests.json.
	loop.json is used to describe the target subsystem(s) hierarchies.
	nvmftests.json used to specify the testcase execution related options.
	For loop mode we create and build loopback device prior to each testcase.
	The number of distinct loopback devices used in loop.json should match
	the "nr_devices" parameter in nvmftests.json.

8. Dependencies
----------------

    6.1. Python(>= 2.7.5 or >= 3.3)
    6.2. nose(http://nose.readthedocs.io/en/latest/)
    6.3. nose2(Installation guide http://nose2.readthedocs.io/)
    6.4. pep8(https://pypi.python.org/pypi/setuptools-pep8)
    6.5. flake8(https://pypi.python.org/pypi/flake8)
    6.6. pylint(https://www.pylint.org/)
    6.7. Epydoc(http://epydoc.sourceforge.net/)
    6.8. nvme-cli(https://github.com/linux-nvme/nvme-cli.git)

    Python package management system pip can be used to install most of the
    listed packages(https://pip.pypa.io/en/stable/installing/) :-

    $ pip install nose nose2 natsort pep8 flake8 pylint epydoc

9. Future Work
--------------

    7.1. Add support for thread safe logging.
    7.2. Improve error handling for host namespaces.
    7.3. Improve support for parallel command submission and return code.
    7.4. Report generation mechanism.
    7.5  Add support for better testcase configuration.
