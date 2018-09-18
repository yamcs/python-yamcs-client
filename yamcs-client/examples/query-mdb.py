from __future__ import print_function

from yamcs.client import YamcsClient

client = YamcsClient('localhost:8090')

mdb = client.get_mdb(instance='simulator')

for parameter in mdb.list_parameters(parameter_type='float'):
    print(parameter.qualified_name)

print('---')

p1 = mdb.get_parameter('/YSS/SIMULATOR/BatteryVoltage2')
p2 = mdb.get_parameter('MDB:OPS Name/SIMULATOR_BatteryVoltage2')

# Should be same
print(p1.qualified_name)
print(p2.qualified_name)
