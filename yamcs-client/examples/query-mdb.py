from __future__ import print_function

from yamcs import YamcsClient

client = YamcsClient('localhost:8090')

mdb = client.get_mdb(instance='simulator')

for parameter in mdb.list_parameters(parameter_type='float'):
    print(parameter.qualifiedName)

print('---')

p1 = mdb.get_parameter('/YSS/SIMULATOR/BatteryVoltage2')
p2 = mdb.get_parameter('MDB:OPS Name/SIMULATOR_BatteryVoltage2')

# Should be same
print(p1.qualifiedName)
print(p2.qualifiedName)
