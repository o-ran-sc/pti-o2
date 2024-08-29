.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. Copyright (C) 2021-2022 Wind River Systems, Inc.

.. _api_docs:

.. |swagger-icon| image:: ./images/swagger.png
                  :width: 40px

.. |yaml-icon| image:: ./images/yaml_logo.png
                  :width: 40px


O-RAN O2 API Definition v1
==========================

This document defines how a SMO like application can perform the management 
of O-Cloud infrastructures and the deployment life cycle management of O-RAN 
cloudified NFs that run on O-Cloud via O-RAN O2 interfaces.

The typical port used for the O-RAN O2 REST API is 30205. 

Here we describe the API to access the O2 API.


O2 API v1
---------

The O2 API v1 provides API includes O2ims_InfrastructureInventory, O2ims_InfrastructureMonitoring and
Kubernetes native API based O2dms interfaces.

See `O-RAN O2 API v1 <./oran-o2-api.html>`_ for full details of the API.

The API is also described in Swagger-JSON and YAML:


.. csv-table::
   :header: "API name", "|swagger-icon|", "|yaml-icon|"
   :widths: 10,5, 5

   "O-RAN O2 API", ":download:`link <./swagger.json>`", ":download:`link <./swagger.yaml>`"
