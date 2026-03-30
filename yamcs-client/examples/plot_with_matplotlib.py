from datetime import datetime, timedelta, timezone

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from yamcs.client import YamcsClient

if __name__ == "__main__":
    client = YamcsClient("localhost:8090")
    archive = client.get_archive(instance="simulator")

    stop = datetime.now(tz=timezone.utc)
    start = stop - timedelta(hours=1)

    samples = archive.downsample_mean("/YSS/SIMULATOR/Altitude", start=start, stop=stop)
    x = [s.time for s in samples]
    y = [s.avg for s in samples]

    mx = [mdates.date2num(t) for t in x]
    my = [val if val is not None else float("nan") for val in y]

    plt.subplot(2, 1, 1)
    plt.title("Sampled at " + str(stop))
    plt.plot(mx, my)
    plt.xlim(start, stop)
    plt.ylabel("Altitude")
    plt.grid()
    plt.xticks(rotation=45, ha="right")

    samples = archive.downsample_mean("/YSS/SIMULATOR/SinkRate", start=start, stop=stop)
    x = [s.time for s in samples]
    y = [s.avg for s in samples]

    mx = [mdates.date2num(t) for t in x]
    my = [val if val is not None else float("nan") for val in y]

    plt.subplot(2, 1, 2)
    plt.plot(mx, my)
    plt.xlim(start, stop)
    plt.xlabel("UTC")
    plt.ylabel("Sink Rate")
    plt.grid()
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.show()
