from yamcs.management import ManagementClient
from yamcs.mdb import MDBClient

mdb_client = MDBClient('localhost', 8090)

instance = 'simulator'
mdb_name = MDBClient.mdb_path(instance)

for parameter in mdb_client.list_parameters(mdb_name, parameter_type='float'):
    print parameter.qualifiedName

print '---'

pname = MDBClient.parameter_path(instance, '/YSS/SIMULATOR/BatteryVoltage2')
print mdb_client.get_parameter(pname).qualifiedName

print '---'
alias = MDBClient.name_alias('MDB:OPS Name', 'SIMULATOR_BatteryVoltage2')
pname = MDBClient.parameter_path(instance, alias)
print mdb_client.get_parameter(pname).qualifiedName

print '---'

management_client = ManagementClient('localhost', 8090)
for link in management_client.list_data_links('simulator'):
    print link.name
