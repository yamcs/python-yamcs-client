from yamcs.client import YamcsClient


def create_bands():
    """Snippet used in docs to create a few bands."""
    global utc_time, local_time, group_a, group_b
    from yamcs.client import ItemBand, TimeRuler

    utc_time = TimeRuler()
    utc_time.name = "UTC"
    timeline.save_band(utc_time)

    local_time = TimeRuler()
    local_time.name = "Local"
    local_time.timezone = "Europe/Brussels"
    timeline.save_band(local_time)

    group_a = ItemBand()
    group_a.name = "Group A"
    group_a.tags = ["group-a"]
    timeline.save_band(group_a)

    group_b = ItemBand()
    group_b.name = "Group B"
    group_b.tags = ["group-b"]
    group_b.item_border_color = "#ff4500"
    group_b.item_background_color = "#ffa500"
    timeline.save_band(group_b)


def create_items():
    """Snippet used in docs to create a few items."""
    from datetime import datetime, timedelta, timezone

    from yamcs.client import Item

    now = datetime.now(tz=timezone.utc)

    for i in range(10):
        item = Item()
        item.name = f"A {i + 1}"
        item.start = now + timedelta(seconds=i * 7200)
        item.duration = timedelta(seconds=3600)
        item.tags = ["group-a"]
        timeline.save_item(item)

        item = Item()
        item.name = f"B {i + 1}"
        item.start = now + timedelta(seconds=3600 + (i * 7200))
        item.duration = timedelta(seconds=3600)
        item.tags = ["group-b"]
        timeline.save_item(item)


def create_view():
    """Snippet used in docs to create a view."""
    from yamcs.client import View

    view = View()
    view.name = "Two groups"
    view.bands = [utc_time, local_time, group_a, group_b]
    timeline.save_view(view)


def edit_band():
    """Snippet used in docs to edit a band."""
    global group_a
    group_a.description = "A few random items"
    timeline.save_band(group_a)


def edit_fetched_items():
    """Snippet used in docs to edit a fetched band."""
    for item in timeline.list_items():
        item.tags.append("example")
        timeline.save_item(item)


def create_parameter_bands():
    """Snippet used in docs to create parameter-based bands."""
    from yamcs.client import (
        ParameterPlot,
        ParameterStateBand,
        RangeMapping,
        Trace,
        ValueMapping,
        View,
    )

    states = ParameterStateBand()
    states.name = "State example"
    states.parameter = "/YSS/SIMULATOR/BatteryVoltage2"
    states.mappings.append(RangeMapping(40, 56, label="LOW", color="#ff0000"))
    states.mappings.append(ValueMapping(57, label="OK", color="#00ff00"))
    states.mappings.append(RangeMapping(58, 70, label="HIGH", color="#ff0000"))
    timeline.save_band(states)

    plot = ParameterPlot()
    plot.name = "Plot example"
    plot.maximum = 65
    trace = Trace(
        parameter="/YSS/SIMULATOR/BatteryVoltage2",
        line_color="#ffff00",
        fill=True,
    )
    plot.traces.append(trace)
    timeline.save_band(plot)

    view = View()
    view.name = "Parameter examples"
    view.bands = [states, plot]
    timeline.save_view(view)


if __name__ == "__main__":
    client = YamcsClient("localhost:8090")
    timeline = client.get_timeline_client("simulator")

    # Delete all
    for view in timeline.list_views():
        timeline.delete_view(view.id)
    for band in timeline.list_bands():
        timeline.delete_band(band.id)
    for item in timeline.list_items():
        timeline.delete_item(item.id)

    create_bands()
    create_items()
    create_view()
    edit_band()
    edit_fetched_items()
    create_parameter_bands()
