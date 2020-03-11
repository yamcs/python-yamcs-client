from time import sleep

from yamcs.client import YamcsClient


def subscribe_param():
    """Print value of parameter"""
    def print_data(data):
        for parameter in data.parameters:
            print(parameter)

    processor.create_parameter_subscription('/YSS/SIMULATOR/battery_voltage_avg',
                                            on_data=print_data)


def set_algorithm():
    processor.set_algorithm('/YSS/SIMULATOR/Battery_Voltage_Avg',
                            text='r.value = 10*(b1.value + b2.value+b3.value)')


def reset_algorithm():
    processor.reset_algorithm('/YSS/SIMULATOR/Battery_Voltage_Avg')


if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    processor = client.get_processor(instance='simulator',
                                     processor='realtime')

    subscribe_param()
    sleep(5)
    print('Set new algo')
    set_algorithm()
    sleep(10)
    print('reset algo to the MDB definition')
    reset_algorithm()
    sleep(10)
