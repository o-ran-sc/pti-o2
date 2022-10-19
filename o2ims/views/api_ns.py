from flask_restx import Namespace


api_ims_inventory_v1 = Namespace(
    "O2IMS_Inventory",
    description='IMS Inventory related operations.')

api_provision_v1 = Namespace(
    "PROVISION",
    description='Provision related operations.')

api_monitoring_v1 = Namespace(
    "O2IMS_InfrastructureMonitoring",
    description='O2 IMS Monitoring related operations.')
