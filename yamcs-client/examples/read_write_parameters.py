# fmt: off
from yamcs.client import YamcsClient


def print_cached_value():
    """Print a single value from server cache."""
    pval = processor.get_parameter_value('/YSS/SIMULATOR/BatteryVoltage1')
    print(pval)


def print_realtime_value():
    """Print a newly processed value."""
    pval = processor.get_parameter_value('/YSS/SIMULATOR/BatteryVoltage2',
                                         from_cache=False, timeout=5)
    print(pval)


def print_current_values():
    """Print multiple parameters from server cache."""
    pvals = processor.get_parameter_values([
        '/YSS/SIMULATOR/BatteryVoltage1',
        '/YSS/SIMULATOR/BatteryVoltage2',
    ])
    print('battery1', pvals[0])
    print('battery2', pvals[1])


def write_value():
    """Writes to a software parameter."""
    processor.set_parameter_value('/YSS/SIMULATOR/AllowCriticalTC1', True)


def write_values():
    """Writes multiple software parameters."""
    processor.set_parameter_values({
        '/YSS/SIMULATOR/AllowCriticalTC1': False,
        '/YSS/SIMULATOR/AllowCriticalTC2': False,
    })


if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    processor = client.get_processor(instance='simulator',
                                     processor='realtime')

    print('Fetch parameter value from cache')
    print_cached_value()

    print('\nFetch newly processed parameter value')
    print_realtime_value()

    print('\nFetch multiple parameters at the same time')
    print_current_values()

    print('\nWrite to a software parameter')
    write_value()

    print('\nWrite multiple software parameters at once')
    write_values()
