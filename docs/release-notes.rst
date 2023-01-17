.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. Copyright (C) 2021-2022 Wind River Systems, Inc.


Release-notes
=============


This document provides the release notes for 1.0.1 of INF O2 service.

.. contents::
   :depth: 3
   :local:


Version History
---------------

+------------+----------+---------------------+-------------+
| **Date**   | **Ver.** | **Author**          | **Comment** |
+------------+----------+---------------------+-------------+
| 2022-06-15 | 1.0.1    | Bin Yang, Jon Zhang | F Release   |
+------------+----------+---------------------+-------------+
| 2021-12-15 | 1.0.0    | Bin Yang, Jon Zhang | E Release   |
+------------+----------+---------------------+-------------+

Version 1.0.1, 2022-06-15
-------------------------

-  Add Distributed Cloud(DC) supported

   -  Enable multiple ResourcePool support in DC mode
   -  Enable multiple DeploymentManager support in DC mode

-  Add O2 DMS profiles

   -  Support native_k8sapi profile that can get native Kubernetes API information
   -  Support SOL018 specification, it includes native Kubernetes API profile and Helm CLI profile, "sol018", and "sol018_helmcli"

Version 1.0.0, 2021-12-15
-------------------------

-  Initial version (E release)
-  Add O2 IMS for INF platform

   -  Enable INF platform registration to SMO
   -  Enable O2 infrastructure inventory service API
   -  Enable O2 Subscription service API
   -  Enable O2 Notification service to notify SMO about the resource
      changes

-  ADD O2 DMS for INF platform

   -  A PoC which enables Lifecycle management of NfDeployment
      represents CNF described with helm chart
   -  Add Lifecycle Management API for NfDeploymentDescriptor which
      represents a helm chart for NfDeployment
   -  Add Lifecycle Management API for NfDeployment
