from __future__ import print_function

from time import sleep

from yamcs import YamcsClient


def print_value(data):
    for parameter in data.parameter:
        print('{} {} {}'.format(parameter.generationTimeUTC, parameter.id.name,
                                parameter.engValue.uint32Value))


if __name__ == '__main__':
    client = YamcsClient('localhost:8090')

    processor = client.get_processor('simulator', 'realtime')
    subscription = processor.create_parameter_subscription([
        '/YSS/SIMULATOR/BatteryVoltage1',
    ], on_data=print_value)

    sleep(5)

    subscription.add([
        '/YSS/SIMULATOR/Alpha',
        '/YSS/SIMULATOR/BatteryVoltage2',
        'MDB:OPS Name/SIMULATOR_PrimBusVoltage1',
    ])

    sleep(5)

    subscription.remove('/YSS/SIMULATOR/Alpha')

    sleep(10)
