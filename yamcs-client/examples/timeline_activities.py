from datetime import datetime

from yamcs.client import YamcsClient


def chain_activities():
    """Snippet used in docs."""
    from yamcs.client import (
        CommandActivity,
        OnSuccess,
        ScriptActivity,
        TimelineActivity,
    )

    # Define the first activity (The Predecessor)
    item_a = TimelineActivity(
        name="Data Dump",
        start=datetime.now(),
        activity=CommandActivity(command="/SPACECRAFT/DUMP_DATA"),
    )

    # Define the second activity, triggered by the success of the first
    item_b = TimelineActivity(
        name="Cleanup",
        start=OnSuccess(item_a),
        activity=ScriptActivity(script="cleanup.sh"),
    )

    # Save both to the timeline
    timeline.save_item(item_a)
    timeline.save_item(item_b)


if __name__ == "__main__":
    client = YamcsClient("localhost:8090")
    timeline = client.get_timeline_client("simulator")
    chain_activities()
