from time import sleep

from yamcs.client import YamcsClient


def enable_link(link):
    """Enable a link."""
    link.enable_link()


def run_action(link, action_id, message=None):
    """Run an action."""
    link.run_action(action_id, message)


if __name__ == "__main__":
    client = YamcsClient("localhost:8090")
    link = client.get_link("simulator", link="tm_dump")

    print("Enabling link")
    enable_link(link)

    subscription = client.create_link_subscription("simulator")

    sleep(10)

    print("-----")
    # Retrieve the latest data link state from local cache:
    print("Last values from cache:")
    for link in subscription.list_links():
        print(link)
