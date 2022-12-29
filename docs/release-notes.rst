.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. Copyright (C) 2021-2022 Wind River Systems, Inc.


Release-notes
=============


This document provides the release notes for 2.0.1 of INF O2 service.

.. contents::
   :depth: 3
   :local:


Version History
---------------

+------------+----------+----------------------------------------------+-------------+
| **Date**   | **Ver.** | **Author**                                   | **Comment** |
+------------+----------+----------------------------------------------+-------------+
| 2022-12-15 | 2.0.1    | Bin Yang, Jon Zhang, Jackie Huang, David Liu | G Release   |
+------------+----------+----------------------------------------------+-------------+
| 2022-06-15 | 1.0.1    | Bin Yang, Jon Zhang                          | F Release   |
+------------+----------+----------------------------------------------+-------------+
| 2021-12-15 | 1.0.0    | Bin Yang, Jon Zhang                          | E Release   |
+------------+----------+----------------------------------------------+-------------+

Version 2.0.1, 2022-12-15
-------------------------

-  Upgrade Inventory API, and add Monitoring API

   -  Support HTTPS and token validation of API
   -  Add "api_version" query in base API
   -  Add "O2IMS_InfrastructureMonitoring" API part
   -  Support Attribute-based selectors, and API query filter parameters
      following the specification
   -  Updating error handling of all the API queries

-  Update the Subscription and Notification part

   -  Notification SMO and register O-Cloud when the application starts
      with SMO configuration
   -  Support subscription inventory change or alarm notification with
      the filter parameter

-  Specification compliance

   -  Compliance to "O-RAN.WG6.O2IMS-INTERFACEv03.0"
   -  Updating modeling, including ResourcePool, ResourceInfo,
      DeploymentManager, ResourceType, Notification, O-Cloud,
      AlarmEventRecord, AlarmDictorary, and AlarmDefinition
   -  Adding Accelerators as a resource; adding virtual resource type

-  Other updates

   -  Add configuration file load at application starts
   -  Fix bugs
   -  Replace POC O2DMS APIs with Kubernetes Native API Profile 
      for Containerized NFs

Version 1.0.1, 2022-06-15
-------------------------

-  Add Distributed Cloud(DC) supported

   -  Enable multiple ResourcePool support in DC mode
   -  Enable multiple DeploymentManager support in DC mode

-  Add O2 DMS profiles

   -  Support native_k8sapi profile
   -  Support SOL018 and Helm CLI profile, "sol018", and "sol018_helmcli"

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
