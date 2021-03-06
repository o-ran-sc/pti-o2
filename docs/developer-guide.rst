.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. Copyright (C) 2021 Wind River Systems, Inc.

Developer-Guide
===============

.. contents::
   :depth: 3
   :local:


This project implements a reference implementation for O-RAN O2 IMS and DMS to expose the INF platform to SMO with the O2 interface.

To contribute to this project, you are supposed to be familiar with the INF platform as well as O-RAN O2 interface specifications:

- `O-RAN SC INF platfrom`_
- `O-RAN O2 interface`_

.. _`O-RAN SC INF platfrom`: https://docs.o-ran-sc.org/en/latest/projects.html#infrastructure-inf
.. _`O-RAN O2 interface`: https://oranalliance.atlassian.net/wiki/spaces/COWG/overview



1. Prerequisite for building environment
----------------------------------------

* A ubuntu 18.04 host is sufficient to build o2 projects

.. code:: shell

  # clone code from gerrit repo
  $ git clone "https://gerrit.o-ran-sc.org/r/pti/o2" && (cd "o2" && mkdir -p .git/hooks && curl -Lo `git rev-parse --git-dir`/hooks/commit-msg https://gerrit.o-ran-sc.org/r/tools/hooks/commit-msg; chmod +x `git rev-parse --git-dir`/hooks/commit-msg)
  # run unit tests
  $ sudo apt-get install tox
  $ tox -e flake8
  $ tox -e code


2. Local test with docker-compose
---------------------------------

* To test with docker-compose, a docker engine is supposed to be installed as well

.. code:: shell

  $ docker-compose build
  $ docker-compose up -d
  $ docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit /tests/integration


3. Test with INF platform
-------------------------

* To test with INF platform, you should install INF platform first, by default you will be able to use the 'admin' user

.. code:: shell

  $ source ./admin_openrc.sh
  $ export |grep OS_AUTH_URL
  $ export |grep OS_USERNAME
  $ export |grep OS_PASSWORD
  $ docker-compose run --rm --no-deps --entrypoint=pytest api /tests/integration-ocloud --log-level=DEBUG --log-file=/tests/debug.log

4. Tear down docker containers
------------------------------

.. code:: shell

  $ docker-compose down --remove-orphans
