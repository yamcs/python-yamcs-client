from __future__ import print_function

from yamcs.mdb import MDBClient

client = MDBClient('localhost:8090')

instance = 'simulator'
mdb_name = client.mdb_path(instance)

for parameter in client.list_parameters(mdb_name, parameter_type='float'):
    print(parameter.qualifiedName)

print('---')

pname = MDBClient.parameter_path(instance, '/YSS/SIMULATOR/BatteryVoltage2')
print(client.get_parameter(pname).qualifiedName)

print('---')
alias = MDBClient.name_alias('MDB:OPS Name', 'SIMULATOR_BatteryVoltage2')
pname = MDBClient.parameter_path(instance, alias)
print(client.get_parameter(pname).qualifiedName)
