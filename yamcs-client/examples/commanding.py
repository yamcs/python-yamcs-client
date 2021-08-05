from time import sleep

from yamcs.client import YamcsClient
from yamcs.tmtc.model import VerificationConfig


def issue_command():
    """Issue a command to turn battery 1 off."""
    command = processor.issue_command(
        "/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF", args={"voltage_num": 1}
    )
    print("Issued", command)


def issue_command_modify_verification():
    """Issue a command with changed verification."""
    verification = VerificationConfig()
    verification.disable("Started")
    verification.modify_check_window("Queued", 1, 5)

    command = processor.issue_command(
        "/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF",
        args={"voltage_num": 1},
        verification=verification,
    )

    print("Issued", command)


def issue_command_no_verification():
    """Issue a command with no verification."""
    verification = VerificationConfig()
    verification.disable()

    command = processor.issue_command(
        "/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF",
        args={"voltage_num": 1},
        verification=verification,
    )

    print("Issued", command)


def monitor_command():
    """Monitor command completion."""
    conn = processor.create_command_connection()

    command1 = conn.issue("/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF", args={"voltage_num": 1})

    # Issue 2nd command only if the previous command was completed successfully.
    command1.await_complete()
    if command1.is_success():
        conn.issue("/YSS/SIMULATOR/SWITCH_VOLTAGE_ON", args={"voltage_num": 1})
    else:
        print("Command 1 failed:", command1.error)


def monitor_acknowledgment():
    """Monitor command acknowledgment."""
    conn = processor.create_command_connection()

    command = conn.issue("/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF", args={"voltage_num": 1})

    ack = command.await_acknowledgment("Acknowledge_Sent")
    print(ack.status)


def listen_to_command_history():
    """Receive updates on command history updates."""

    def tc_callback(rec):
        print("TC:", rec)

    processor.create_command_history_subscription(on_data=tc_callback)


def tm_callback(delivery):
    for parameter in delivery.parameters:
        print("TM:", parameter)


if __name__ == "__main__":
    client = YamcsClient("localhost:8090")
    processor = client.get_processor("simulator", "realtime")

    print("Start to listen to command history")
    listen_to_command_history()

    print("Issue a command")
    issue_command()

    # Monitor the voltage parameter to confirm that it is 0
    subscription = processor.create_parameter_subscription(
        ["/YSS/SIMULATOR/BatteryVoltage1"], on_data=tm_callback
    )

    # Subscription is non-blocking
    sleep(20)
