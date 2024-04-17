from yamcs.client import YamcsClient


def run_script():
    """Example used in docs to run a script"""

    # Simulate LOS for 5 seconds
    # (the run_script call does not block)
    processor.run_script("simulate_los.py", "--duration 5")


if __name__ == "__main__":
    client = YamcsClient("localhost:8090")
    processor = client.get_processor("simulator", "realtime")
    run_script()
