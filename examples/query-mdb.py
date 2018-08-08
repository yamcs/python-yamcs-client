from __future__ import print_function

from yamcs.mdb import MDBClient

client = MDBClient('localhost:8090')

instance = 'simulator'
mdb = client.mdb_path(instance)

for parameter in client.list_parameters(mdb, parameter_type='float'):
    print(parameter.qualifiedName)

print('---')

p1 = client.get_parameter(mdb, '/YSS/SIMULATOR/BatteryVoltage2')

alias = client.name_alias('MDB:OPS Name', 'SIMULATOR_BatteryVoltage2')
p2 = client.get_parameter(mdb, alias)

# Should be same
print(p1.qualifiedName)
print(p2.qualifiedName)
