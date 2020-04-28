# fmt: off
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from yamcs.client import YamcsClient

if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    archive = client.get_archive(instance='simulator')

    stop = datetime.utcnow()
    start = stop - timedelta(hours=1)

    samples = archive.sample_parameter_values(
        '/YSS/SIMULATOR/Altitude', start=start, stop=stop)
    x = [s.time for s in samples]
    y = [s.avg for s in samples]
    plt.subplot(2, 1, 1)
    plt.title('Sampled at ' + str(stop))
    plt.plot(x, y)
    plt.ylabel('Altitude')
    plt.grid()

    samples = archive.sample_parameter_values(
        '/YSS/SIMULATOR/SinkRate', start=start, stop=stop)
    x = [s.time for s in samples]
    y = [s.avg for s in samples]
    plt.subplot(2, 1, 2)
    plt.plot(x, y)
    plt.xlabel('UTC')
    plt.ylabel('Sink Rate')
    plt.grid()

    plt.gcf().canvas.set_window_title('Launch & Landing Simulator')
    plt.show()
