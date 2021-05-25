from binascii import hexlify
from time import sleep

from yamcs.client import YamcsClient


def receive_callbacks():
    """Shows how to receive callbacks on packet updates."""

    def print_data(packet):
        hexpacket = hexlify(packet.binary).decode("ascii")
        print(packet.generation_time, ":", hexpacket)

    processor.create_packet_subscription(on_data=print_data)


if __name__ == "__main__":
    client = YamcsClient("localhost:8090")
    processor = client.get_processor("simulator", "realtime")

    print("\nReceive callbacks")
    receive_callbacks()

    sleep(5)  # Subscription is non-blocking
