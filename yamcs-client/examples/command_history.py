from time import sleep

from yamcs.client import YamcsClient

# This demonstrates how to use a single command history subscription to
# follow the acknowledgments of multiple commands.

if __name__ == "__main__":
    client = YamcsClient("localhost:8090")
    processor = client.get_processor("simulator", "realtime")

    # Start to listen to command history
    history_subscription = processor.create_command_history_subscription()

    commands = []

    # Submit a few commands
    for i in range(5):
        command = processor.issue_command(
            "/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF", args={"voltage_num": 1}
        )
        commands.append(command)
        print("Issued", command)

        command = processor.issue_command(
            "/YSS/SIMULATOR/SWITCH_VOLTAGE_ON", args={"voltage_num": 1}
        )
        commands.append(command)
        print("Issued", command)

    while True:
        print("------")
        for command in commands:
            cmdhistory = history_subscription.get_command_history(command)
            print(cmdhistory)
        sleep(5)
