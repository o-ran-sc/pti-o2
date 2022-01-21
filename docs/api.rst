.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. Copyright (C) 2021 Wind River Systems, Inc.

INF O2 Services API 1.0.0
=============================

.. toctree::
    :maxdepth: 3


Description
~~~~~~~~~~~

Swagger OpenAPI document for the INF O2 Services





Base URL
~~~~~~~~

http(s)://<OAM IP>:30205/

O2DMS_LCM
~~~~~~~~~


DMS LCM related operations.





POST ``/o2dms/v1/{deploymentManagerID}/O2dms_DeploymentLifecycle/NfDeployment``
-------------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        deploymentManagerID | path | Yes | string |  |  | ID of the deployment manager


Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask



.. _d_1cdf8e618b9847878bed90d4897e6b3a:

Body
^^^^

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        description | No | string |  |  | 
        descriptorId | No | string |  |  | 
        name | No | string |  |  | 
        parentDeploymentId | No | string |  |  | 

.. code-block:: javascript

    {
        "description": "somestring",
        "descriptorId": "somestring",
        "name": "somestring",
        "parentDeploymentId": "somestring"
    }

Responses
+++++++++

**201**
^^^^^^^

Success


Type: :ref:`NfDeploymentCreateRespDto <d_c00d46ffd3e149e2989d2a5264585581>`

**Example:**

.. code-block:: javascript

    {
        "id": "somestring"
    }

**404**
^^^^^^^

DMS LCM not found






POST ``/o2dms/v1/{deploymentManagerID}/O2dms_DeploymentLifecycle/NfDeploymentDescriptor``
-----------------------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        deploymentManagerID | path | Yes | string |  |  | ID of the deployment manager


Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask



.. _d_1583b74cb6544a428fadd82cb4ff4b3b:

Body
^^^^

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        artifactName | No | string |  |  | 
        artifactRepoUrl | No | string |  |  | 
        description | No | string |  |  | 
        inputParams | No | string |  |  | 
        name | No | string |  |  | 
        outputParams | No | string |  |  | 

.. code-block:: javascript

    {
        "artifactName": "somestring",
        "artifactRepoUrl": "somestring",
        "description": "somestring",
        "inputParams": "somestring",
        "name": "somestring",
        "outputParams": "somestring"
    }

Responses
+++++++++

**201**
^^^^^^^

Success


Type: :ref:`NfDeploymentDescriptorCreateRespDto <d_67c3fe14b244e803ad34a57f27b4bb4e>`

**Example:**

.. code-block:: javascript

    {
        "id": "somestring"
    }

**404**
^^^^^^^

DMS LCM not found






DELETE ``/o2dms/v1/{deploymentManagerID}/O2dms_DeploymentLifecycle/NfDeployment/{nfDeploymentId}``
--------------------------------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        nfDeploymentId | path | Yes | string |  |  | ID of the NfDeployment
        deploymentManagerID | path | Yes | string |  |  | ID of the deployment manager


Request
+++++++


Responses
+++++++++

**204**
^^^^^^^

NfDeployment deleted


**404**
^^^^^^^

DMS LCM not found






DELETE ``/o2dms/v1/{deploymentManagerID}/O2dms_DeploymentLifecycle/NfDeploymentDescriptor/{nfDeploymentDescriptorId}``
----------------------------------------------------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        nfDeploymentDescriptorId | path | Yes | string |  |  | ID of the NfDeploymentDescriptor
        deploymentManagerID | path | Yes | string |  |  | ID of the deployment manager


Request
+++++++


Responses
+++++++++

**204**
^^^^^^^

NfDeploymentDescriptor deleted


**404**
^^^^^^^

DMS LCM not found






GET ``/o2dms/v1/{deploymentManagerID}/O2dms_DeploymentLifecycle/NfDeployment/{nfDeploymentId}``
-----------------------------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        nfDeploymentId | path | Yes | string |  |  | ID of the NfDeployment
        deploymentManagerID | path | Yes | string |  |  | ID of the deployment manager


Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: :ref:`NfDeploymentGetDto <d_e28dc7c38126e125615678304c7a9508>`

**Example:**

.. code-block:: javascript

    {
        "description": "somestring",
        "descriptorId": "somestring",
        "id": "somestring",
        "name": "somestring",
        "parentDeploymentId": "somestring",
        "status": 1
    }

**404**
^^^^^^^

DMS LCM not found






GET ``/o2dms/v1/{deploymentManagerID}/O2dms_DeploymentLifecycle/NfDeploymentDescriptor/{nfDeploymentDescriptorId}``
-------------------------------------------------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        nfDeploymentDescriptorId | path | Yes | string |  |  | ID of the NfDeploymentDescriptor
        deploymentManagerID | path | Yes | string |  |  | ID of the deployment manager


Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: :ref:`NfDeploymentDescriptorGetDto <d_5bdce8ac307530aa532cc25654cd5b07>`

**Example:**

.. code-block:: javascript

    {
        "artifactName": "somestring",
        "artifactRepoUrl": "somestring",
        "description": "somestring",
        "id": "somestring",
        "inputParams": "somestring",
        "name": "somestring",
        "outputParams": "somestring"
    }

**404**
^^^^^^^

DMS LCM not found






GET ``/o2dms/v1/{deploymentManagerID}/O2dms_DeploymentLifecycle/NfDeployment``
------------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        deploymentManagerID | path | Yes | string |  |  | ID of the deployment manager


Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: array of :ref:`NfDeploymentGetDto <d_e28dc7c38126e125615678304c7a9508>`


**Example:**

.. code-block:: javascript

    [
        {
            "description": "somestring",
            "descriptorId": "somestring",
            "id": "somestring",
            "name": "somestring",
            "parentDeploymentId": "somestring",
            "status": 1
        },
        {
            "description": "somestring",
            "descriptorId": "somestring",
            "id": "somestring",
            "name": "somestring",
            "parentDeploymentId": "somestring",
            "status": 1
        }
    ]

**404**
^^^^^^^

DMS LCM not found






GET ``/o2dms/v1/{deploymentManagerID}/O2dms_DeploymentLifecycle/NfDeploymentDescriptor``
----------------------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        deploymentManagerID | path | Yes | string |  |  | ID of the deployment manager


Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: array of :ref:`NfDeploymentDescriptorGetDto <d_5bdce8ac307530aa532cc25654cd5b07>`


**Example:**

.. code-block:: javascript

    [
        {
            "artifactName": "somestring",
            "artifactRepoUrl": "somestring",
            "description": "somestring",
            "id": "somestring",
            "inputParams": "somestring",
            "name": "somestring",
            "outputParams": "somestring"
        },
        {
            "artifactName": "somestring",
            "artifactRepoUrl": "somestring",
            "description": "somestring",
            "id": "somestring",
            "inputParams": "somestring",
            "name": "somestring",
            "outputParams": "somestring"
        }
    ]

**404**
^^^^^^^

DMS LCM not found






GET ``/o2dms/v1/{deploymentManagerID}``
---------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        deploymentManagerID | path | Yes | string |  |  | ID of the deployment manager


Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: :ref:`DmsGetDto <d_086ee84f2c2cf010478bfc73a87b5e80>`

**Example:**

.. code-block:: javascript

    {
        "capabilities": "somestring",
        "capacity": "somestring",
        "deploymentManagerId": "somestring",
        "description": "somestring",
        "name": "somestring",
        "supportedLocations": "somestring"
    }

**404**
^^^^^^^

Deployment manager not found






PUT ``/o2dms/v1/{deploymentManagerID}/O2dms_DeploymentLifecycle/NfDeployment/{nfDeploymentId}``
-----------------------------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        nfDeploymentId | path | Yes | string |  |  | ID of the NfDeployment
        deploymentManagerID | path | Yes | string |  |  | ID of the deployment manager


Request
+++++++



.. _d_1a0e59d24d7db279637f186c203d883d:

Body
^^^^

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        description | No | string |  |  | 
        name | No | string |  |  | 
        parentDeploymentId | No | string |  |  | 

.. code-block:: javascript

    {
        "description": "somestring",
        "name": "somestring",
        "parentDeploymentId": "somestring"
    }

Responses
+++++++++

**404**
^^^^^^^

DMS LCM not found






PUT ``/o2dms/v1/{deploymentManagerID}/O2dms_DeploymentLifecycle/NfDeploymentDescriptor/{nfDeploymentDescriptorId}``
-------------------------------------------------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        nfDeploymentDescriptorId | path | Yes | string |  |  | ID of the NfDeploymentDescriptor
        deploymentManagerID | path | Yes | string |  |  | ID of the deployment manager


Request
+++++++



.. _d_5a6ee319c7ac35eac173da7d57136a98:

Body
^^^^

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        artifactName | No | string |  |  | 
        artifactRepoUrl | No | string |  |  | 
        description | No | string |  |  | 
        inputParams | No | string |  |  | 
        name | No | string |  |  | 
        outputParams | No | string |  |  | 

.. code-block:: javascript

    {
        "artifactName": "somestring",
        "artifactRepoUrl": "somestring",
        "description": "somestring",
        "inputParams": "somestring",
        "name": "somestring",
        "outputParams": "somestring"
    }

Responses
+++++++++

**404**
^^^^^^^

DMS LCM not found




  
O2IMS_INVENTORY
~~~~~~~~~~~~~~~


IMS Inventory related operations.





POST ``/o2ims_infrastructureInventory/v1/subscriptions``
--------------------------------------------------------





Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask



.. _d_0fff8519707c32c34f86d6ac19fad342:

Body
^^^^

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        callback | Yes | string |  |  | Subscription callback address
        consumerSubscriptionId | No | string |  |  | 
        filter | No | string |  |  | 

.. code-block:: javascript

    {
        "callback": "somestring",
        "consumerSubscriptionId": "somestring",
        "filter": "somestring"
    }

Responses
+++++++++

**201**
^^^^^^^

Success


Type: :ref:`SubscriptionCreatedRespDto <d_4397329931bf78862bc91387dbdb86c4>`

**Example:**

.. code-block:: javascript

    {
        "subscriptionId": "somestring"
    }





DELETE ``/o2ims_infrastructureInventory/v1/subscriptions/{subscriptionID}``
---------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        subscriptionID | path | Yes | string |  |  | ID of the subscription


Request
+++++++


Responses
+++++++++

**204**
^^^^^^^

Subscription deleted


**404**
^^^^^^^

Subscription not found






GET ``/o2ims_infrastructureInventory/v1/deploymentManagers/{deploymentManagerID}``
----------------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        deploymentManagerID | path | Yes | string |  |  | ID of the deployment manager


Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: :ref:`DeploymentManagerGetDto <d_e936cc219a004ab92ac027b2690bdd5e>`

**Example:**

.. code-block:: javascript

    {
        "capabilities": "somestring",
        "capacity": "somestring",
        "deploymentManagementServiceEndpoint": "somestring",
        "deploymentManagerId": "somestring",
        "description": "somestring",
        "name": "somestring",
        "supportedLocations": "somestring"
    }

**404**
^^^^^^^

Deployment manager not found






GET ``/o2ims_infrastructureInventory/v1/resourcePools/{resourcePoolID}/resources/{resourceID}``
-----------------------------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        resourceID | path | Yes | string |  |  | ID of the resource
        resourcePoolID | path | Yes | string |  |  | ID of the resource pool


Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: :ref:`ResourceGetDto2 <d_958dd46196a624722ba9ea3ea4d27e38>`

**Example:**

.. code-block:: javascript

    {
        "children": [
            {
                "children": [
                    {
                        "description": "somestring",
                        "elements": "somestring",
                        "name": "somestring",
                        "parentId": "somestring",
                        "resourceId": "somestring",
                        "resourcePoolId": "somestring",
                        "resourceTypeId": "somestring"
                    },
                    {
                        "description": "somestring",
                        "elements": "somestring",
                        "name": "somestring",
                        "parentId": "somestring",
                        "resourceId": "somestring",
                        "resourcePoolId": "somestring",
                        "resourceTypeId": "somestring"
                    }
                ],
                "description": "somestring",
                "elements": "somestring",
                "name": "somestring",
                "parentId": "somestring",
                "resourceId": "somestring",
                "resourcePoolId": "somestring",
                "resourceTypeId": "somestring"
            },
            {
                "children": [
                    {
                        "description": "somestring",
                        "elements": "somestring",
                        "name": "somestring",
                        "parentId": "somestring",
                        "resourceId": "somestring",
                        "resourcePoolId": "somestring",
                        "resourceTypeId": "somestring"
                    },
                    {
                        "description": "somestring",
                        "elements": "somestring",
                        "name": "somestring",
                        "parentId": "somestring",
                        "resourceId": "somestring",
                        "resourcePoolId": "somestring",
                        "resourceTypeId": "somestring"
                    }
                ],
                "description": "somestring",
                "elements": "somestring",
                "name": "somestring",
                "parentId": "somestring",
                "resourceId": "somestring",
                "resourcePoolId": "somestring",
                "resourceTypeId": "somestring"
            }
        ],
        "description": "somestring",
        "elements": "somestring",
        "name": "somestring",
        "parentId": "somestring",
        "resourceId": "somestring",
        "resourcePoolId": "somestring",
        "resourceTypeId": "somestring"
    }

**404**
^^^^^^^

Resource not found






GET ``/o2ims_infrastructureInventory/v1/resourcePools/{resourcePoolID}``
------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        resourcePoolID | path | Yes | string |  |  | ID of the resource pool


Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: :ref:`ResourcePoolGetDto <d_296e5d50362a85c0b8843dfe38965ce9>`

**Example:**

.. code-block:: javascript

    {
        "description": "somestring",
        "globalLocationId": "somestring",
        "location": "somestring",
        "name": "somestring",
        "resourcePoolId": "somestring"
    }

**404**
^^^^^^^

Resource pool not found






GET ``/o2ims_infrastructureInventory/v1/resourceTypes/{resourceTypeID}``
------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        resourceTypeID | path | Yes | string |  |  | ID of the resource type


Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: :ref:`ResourceTypeGetDto <d_fb92075f954e3895d1435d4e523666fa>`

**Example:**

.. code-block:: javascript

    {
        "description": "somestring",
        "name": "somestring",
        "resourceTypeId": "somestring",
        "vendor": "somestring",
        "version": "somestring"
    }

**404**
^^^^^^^

Resource type not found






GET ``/o2ims_infrastructureInventory/v1/subscriptions/{subscriptionID}``
------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        subscriptionID | path | Yes | string |  |  | ID of the subscription


Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: :ref:`SubscriptionGetDto <d_90e532f740e7ec8e9d71fad08513c388>`

**Example:**

.. code-block:: javascript

    {
        "callback": "somestring",
        "consumerSubscriptionId": "somestring",
        "filter": "somestring",
        "subscriptionId": "somestring"
    }

**404**
^^^^^^^

Subscription not found






GET ``/o2ims_infrastructureInventory/v1/subscriptions``
-------------------------------------------------------





Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: array of :ref:`SubscriptionGetDto <d_90e532f740e7ec8e9d71fad08513c388>`


**Example:**

.. code-block:: javascript

    [
        {
            "callback": "somestring",
            "consumerSubscriptionId": "somestring",
            "filter": "somestring",
            "subscriptionId": "somestring"
        },
        {
            "callback": "somestring",
            "consumerSubscriptionId": "somestring",
            "filter": "somestring",
            "subscriptionId": "somestring"
        }
    ]





GET ``/o2ims_infrastructureInventory/v1/deploymentManagers``
------------------------------------------------------------





Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: array of :ref:`DeploymentManagerGetDto <d_e936cc219a004ab92ac027b2690bdd5e>`


**Example:**

.. code-block:: javascript

    [
        {
            "capabilities": "somestring",
            "capacity": "somestring",
            "deploymentManagementServiceEndpoint": "somestring",
            "deploymentManagerId": "somestring",
            "description": "somestring",
            "name": "somestring",
            "supportedLocations": "somestring"
        },
        {
            "capabilities": "somestring",
            "capacity": "somestring",
            "deploymentManagementServiceEndpoint": "somestring",
            "deploymentManagerId": "somestring",
            "description": "somestring",
            "name": "somestring",
            "supportedLocations": "somestring"
        }
    ]





GET ``/o2ims_infrastructureInventory/v1/``
------------------------------------------





Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: :ref:`OcloudDto <d_24d46c2729680edc54e60b2dfbea8ebf>`

**Example:**

.. code-block:: javascript

    {
        "description": "somestring",
        "globalCloudId": "somestring",
        "infrastructureManagementServiceEndpoint": "somestring",
        "name": "somestring",
        "oCloudId": "somestring"
    }

**404**
^^^^^^^

oCloud not found






GET ``/o2ims_infrastructureInventory/v1/resourcePools``
-------------------------------------------------------





Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: array of :ref:`ResourcePoolGetDto <d_296e5d50362a85c0b8843dfe38965ce9>`


**Example:**

.. code-block:: javascript

    [
        {
            "description": "somestring",
            "globalLocationId": "somestring",
            "location": "somestring",
            "name": "somestring",
            "resourcePoolId": "somestring"
        },
        {
            "description": "somestring",
            "globalLocationId": "somestring",
            "location": "somestring",
            "name": "somestring",
            "resourcePoolId": "somestring"
        }
    ]





GET ``/o2ims_infrastructureInventory/v1/resourceTypes``
-------------------------------------------------------





Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: array of :ref:`ResourceTypeGetDto <d_fb92075f954e3895d1435d4e523666fa>`


**Example:**

.. code-block:: javascript

    [
        {
            "description": "somestring",
            "name": "somestring",
            "resourceTypeId": "somestring",
            "vendor": "somestring",
            "version": "somestring"
        },
        {
            "description": "somestring",
            "name": "somestring",
            "resourceTypeId": "somestring",
            "vendor": "somestring",
            "version": "somestring"
        }
    ]





GET ``/o2ims_infrastructureInventory/v1/resourcePools/{resourcePoolID}/resources``
----------------------------------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        parentId | query | No | string |  |  | filter parentId
        resourceTypeName | query | No | string |  |  | filter resource type
        resourcePoolID | path | Yes | string |  |  | ID of the resource pool


Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: array of :ref:`ResourceListDto <d_942ff02bfe350c7d2a7f3faabf5d77d1>`


**Example:**

.. code-block:: javascript

    [
        {
            "description": "somestring",
            "name": "somestring",
            "parentId": "somestring",
            "resourceId": "somestring",
            "resourcePoolId": "somestring",
            "resourceTypeId": "somestring"
        },
        {
            "description": "somestring",
            "name": "somestring",
            "parentId": "somestring",
            "resourceId": "somestring",
            "resourcePoolId": "somestring",
            "resourceTypeId": "somestring"
        }
    ]



  
PROVISION
~~~~~~~~~


Provision related operations.





POST ``/provision/v1/smo-endpoint``
-----------------------------------





Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask



.. _d_18b723a8578a1c0bdb13e962c902ad94:

Body
^^^^

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        endpoint | Yes | string |  |  | Configuration SMO callback address

.. code-block:: javascript

    {
        "endpoint": "somestring"
    }

Responses
+++++++++

**201**
^^^^^^^

Success


Type: :ref:`SmoEndpointCreatedRespDto <d_36a34be9221cecc9bf82d276b9266961>`

**Example:**

.. code-block:: javascript

    {
        "id": "somestring"
    }





DELETE ``/provision/v1/smo-endpoint/{configurationID}``
-------------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        configurationID | path | Yes | string |  |  | ID of the SMO endpoint configuration


Request
+++++++


Responses
+++++++++

**204**
^^^^^^^

Configuration deleted


**404**
^^^^^^^

SMO Endpoint configuration not found






GET ``/provision/v1/smo-endpoint/{configurationID}``
----------------------------------------------------




Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        configurationID | path | Yes | string |  |  | ID of the SMO endpoint configuration


Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: :ref:`SmoEndpointGetDto <d_a6b61d9695be919cc22b2e700eeb7e27>`

**Example:**

.. code-block:: javascript

    {
        "comments": "somestring",
        "endpoint": "somestring",
        "id": "somestring",
        "status": "somestring"
    }

**404**
^^^^^^^

SMO Endpoint configuration not found






GET ``/provision/v1/smo-endpoint``
----------------------------------





Request
+++++++


Headers
^^^^^^^

.. code-block:: javascript

    X-Fields: An optional fields mask


Responses
+++++++++

**200**
^^^^^^^

Success


Type: array of :ref:`SmoEndpointGetDto <d_a6b61d9695be919cc22b2e700eeb7e27>`


**Example:**

.. code-block:: javascript

    [
        {
            "comments": "somestring",
            "endpoint": "somestring",
            "id": "somestring",
            "status": "somestring"
        },
        {
            "comments": "somestring",
            "endpoint": "somestring",
            "id": "somestring",
            "status": "somestring"
        }
    ]



  
Data Structures
~~~~~~~~~~~~~~~

.. _d_e936cc219a004ab92ac027b2690bdd5e:

DeploymentManagerGetDto Model Structure
---------------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        capabilities | No | string |  |  | 
        capacity | No | string |  |  | 
        deploymentManagementServiceEndpoint | No | string |  |  | 
        deploymentManagerId | Yes | string |  |  | Deployment manager ID
        description | No | string |  |  | 
        name | No | string |  |  | 
        supportedLocations | No | string |  |  | 

.. _d_086ee84f2c2cf010478bfc73a87b5e80:

DmsGetDto Model Structure
-------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        capabilities | No | string |  |  | 
        capacity | No | string |  |  | 
        deploymentManagerId | Yes | string |  |  | Deployment manager ID
        description | No | string |  |  | 
        name | No | string |  |  | 
        supportedLocations | No | string |  |  | 

.. _d_1cdf8e618b9847878bed90d4897e6b4a:

NfDeploymentCreateDto Model Structure
-------------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        description | No | string |  |  | 
        descriptorId | No | string |  |  | 
        name | No | string |  |  | 
        parentDeploymentId | No | string |  |  | 

.. _d_c00d46ffd3e149e2989d2a5264585581:

NfDeploymentCreateRespDto Model Structure
-----------------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        id | Yes | string |  |  | NfDeployment ID

.. _d_1583b74cb6544a428fadd82cb4ff4b4b:

NfDeploymentDescriptorCreateDto Model Structure
-----------------------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        artifactName | No | string |  |  | 
        artifactRepoUrl | No | string |  |  | 
        description | No | string |  |  | 
        inputParams | No | string |  |  | 
        name | No | string |  |  | 
        outputParams | No | string |  |  | 

.. _d_67c3fe14b244e803ad34a57f27b4bb4e:

NfDeploymentDescriptorCreateRespDto Model Structure
---------------------------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        id | Yes | string |  |  | NfDeploymentDescriptor ID

.. _d_5bdce8ac307530aa532cc25654cd5b07:

NfDeploymentDescriptorGetDto Model Structure
--------------------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        artifactName | No | string |  |  | 
        artifactRepoUrl | No | string |  |  | 
        description | No | string |  |  | 
        id | Yes | string |  |  | NfDeploymentDescriptor ID
        inputParams | No | string |  |  | 
        name | No | string |  |  | 
        outputParams | No | string |  |  | 

.. _d_5a6ee319c7ac35eac173da7d57136a99:

NfDeploymentDescriptorUpdateDto Model Structure
-----------------------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        artifactName | No | string |  |  | 
        artifactRepoUrl | No | string |  |  | 
        description | No | string |  |  | 
        inputParams | No | string |  |  | 
        name | No | string |  |  | 
        outputParams | No | string |  |  | 

.. _d_e28dc7c38126e125615678304c7a9508:

NfDeploymentGetDto Model Structure
----------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        description | No | string |  |  | 
        descriptorId | No | string |  |  | 
        id | Yes | string |  |  | NfDeployment ID
        name | No | string |  |  | 
        parentDeploymentId | No | string |  |  | 
        status | No | integer |  |  | 

.. _d_1a0e59d24d7db279637f186c203d884d:

NfDeploymentUpdateDto Model Structure
-------------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        description | No | string |  |  | 
        name | No | string |  |  | 
        parentDeploymentId | No | string |  |  | 

.. _d_24d46c2729680edc54e60b2dfbea8ebf:

OcloudDto Model Structure
-------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        description | No | string |  |  | 
        globalCloudId | No | string |  |  | 
        infrastructureManagementServiceEndpoint | No | string |  |  | 
        name | No | string |  |  | 
        oCloudId | Yes | string |  |  | 

.. _d_6d49595cea3e0fa957a06fb11bda4897:

ResourceGetDto0 Model Structure
-------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        description | No | string |  |  | 
        elements | No | string |  |  | 
        name | No | string |  |  | 
        parentId | No | string |  |  | 
        resourceId | Yes | string |  |  | Resource ID
        resourcePoolId | No | string |  |  | 
        resourceTypeId | No | string |  |  | 

.. _d_bb8426c45d4d19dc6128fbb298c7bb4d:

ResourceGetDto1 Model Structure
-------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        children | No | array of :ref:`ResourceGetDto0 <d_6d49595cea3e0fa957a06fb11bda4897>` |  |  | 
        description | No | string |  |  | 
        elements | No | string |  |  | 
        name | No | string |  |  | 
        parentId | No | string |  |  | 
        resourceId | Yes | string |  |  | Resource ID
        resourcePoolId | No | string |  |  | 
        resourceTypeId | No | string |  |  | 

.. _d_958dd46196a624722ba9ea3ea4d27e38:

ResourceGetDto2 Model Structure
-------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        children | No | array of :ref:`ResourceGetDto1 <d_bb8426c45d4d19dc6128fbb298c7bb4d>` |  |  | 
        description | No | string |  |  | 
        elements | No | string |  |  | 
        name | No | string |  |  | 
        parentId | No | string |  |  | 
        resourceId | Yes | string |  |  | Resource ID
        resourcePoolId | No | string |  |  | 
        resourceTypeId | No | string |  |  | 

.. _d_942ff02bfe350c7d2a7f3faabf5d77d1:

ResourceListDto Model Structure
-------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        description | No | string |  |  | 
        name | No | string |  |  | 
        parentId | No | string |  |  | 
        resourceId | Yes | string |  |  | Resource ID
        resourcePoolId | No | string |  |  | 
        resourceTypeId | No | string |  |  | 

.. _d_296e5d50362a85c0b8843dfe38965ce9:

ResourcePoolGetDto Model Structure
----------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        description | No | string |  |  | 
        globalLocationId | No | string |  |  | 
        location | No | string |  |  | 
        name | No | string |  |  | 
        resourcePoolId | Yes | string |  |  | Resource pool ID

.. _d_fb92075f954e3895d1435d4e523666fa:

ResourceTypeGetDto Model Structure
----------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        description | No | string |  |  | 
        name | No | string |  |  | 
        resourceTypeId | Yes | string |  |  | Resource type ID
        vendor | No | string |  |  | 
        version | No | string |  |  | 

.. _d_18b723a8578a1c0bdb13e962c902ad95:

SmoEndpointCreateDto Model Structure
------------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        endpoint | Yes | string |  |  | Configuration SMO callback address

.. _d_36a34be9221cecc9bf82d276b9266961:

SmoEndpointCreatedRespDto Model Structure
-----------------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        id | Yes | string |  |  | SMO Endpoint Configuration ID

.. _d_a6b61d9695be919cc22b2e700eeb7e27:

SmoEndpointGetDto Model Structure
---------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        comments | No | string |  |  | 
        endpoint | No | string |  |  | 
        id | Yes | string |  |  | SMO Endpoint Configuration ID
        status | No | string |  |  | 

.. _d_0fff8519707c32c34f86d6ac19fad343:

SubscriptionCreateDto Model Structure
-------------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        callback | Yes | string |  |  | Subscription callback address
        consumerSubscriptionId | No | string |  |  | 
        filter | No | string |  |  | 

.. _d_4397329931bf78862bc91387dbdb86c4:

SubscriptionCreatedRespDto Model Structure
------------------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        subscriptionId | Yes | string |  |  | Subscription ID

.. _d_90e532f740e7ec8e9d71fad08513c388:

SubscriptionGetDto Model Structure
----------------------------------

.. csv-table::
    :delim: |
    :header: "Name", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 10, 15, 15, 30, 25

        callback | No | string |  |  | 
        consumerSubscriptionId | No | string |  |  | 
        filter | No | string |  |  | 
        subscriptionId | Yes | string |  |  | Subscription ID

