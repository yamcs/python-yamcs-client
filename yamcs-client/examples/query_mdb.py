from yamcs.client import YamcsClient


def print_space_systems():
    """Print all space systems."""
    for space_system in mdb.list_space_systems():
        print(space_system)


def print_parameters():
    """Print all float parameters."""
    for parameter in mdb.list_parameters(parameter_type="float"):
        print(parameter)


def print_commands():
    """Print all commands."""
    for command in mdb.list_commands():
        print(command)


def find_parameter():
    """Find one parameter."""
    p1 = mdb.get_parameter("/YSS/SIMULATOR/BatteryVoltage2")
    print("Via qualified name:", p1)

    p2 = mdb.get_parameter("MDB:OPS Name/SIMULATOR_BatteryVoltage2")
    print("Via domain-specific alias:", p2)


if __name__ == "__main__":
    client = YamcsClient("localhost:8090")
    mdb = client.get_mdb(instance="simulator")

    print("\nSpace systems:")
    print_space_systems()

    print("\nParameters:")
    print_parameters()

    print("\nCommands:")
    print_commands()

    print("\nFind a specific parameter using different names")
    find_parameter()
