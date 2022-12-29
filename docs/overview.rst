.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. Copyright (C) 2021-2022 Wind River Systems, Inc.

INF O2 Service Overview
=======================

This project implements a reference O-RAN O2 IMS and DMS service to
expose the INF platform to SMO via the O-RAN O2 interface.

In the G release, the following APIs are supported by the INF O2
service:

1. INF O2 service Infrastructure Management Service (IMS)

   -  INF O2 service Inventory API

      -  O2 service discovers following resources of INF platform to
         answer queries from SMO

         -  INF platform information
         -  Resource Pool of the INF platform
         -  Resources of the Resource Pool, including pserver, cpu, memory, interface, accelerator
         -  Resource Types associated with Resources

      -  INF platform Subscription and Notification

         -  INF O2 service exposes Subscription API to enable SMO
            subscribes to Notification of changes of resources

      -  INF platform Deployment Management Service profile queries API

         -  INF O2 service enables lookup of INF Native Kubernetes API information as part of inventory

   -  INF O2 service Monitoring API

      -  O2 service discovers alarms of INF platform to answer queries from SMO

         -  INF alarm event record information

      -  INF alarm Subscription and Notification

         -  INF O2 service exposes alarm Subscription API to enable SMO
            subscribes to Notification of changes of alarms

