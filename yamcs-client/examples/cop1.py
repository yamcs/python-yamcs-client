from time import sleep

from yamcs.client import YamcsClient


def callback(status):
    print("<callback> status:", status)


if __name__ == "__main__":
    client = YamcsClient("localhost:8090")
    link = client.get_link("simulator", link="UDP_FRAME_OUT.vc0")

    config = link.get_cop1_config()
    print(config)

    print("Changing COP1 configuration")
    link.update_cop1_config(t1=3.1, tx_limit=4)

    monitor = link.create_cop1_subscription(on_data=callback)
    print("COP1 status subscribed.")

    sleep(5)

    print("Disabling COP1....")
    link.disable_cop1()

    sleep(3)
    print("Initializing COP1 with CLCW_CHECK")
    print("  (if no CLCW is received, COP1 will be suspended in 3 seconds)")
    link.initialize_cop1("WITH_CLCW_CHECK", clcw_wait_timeout=3)

    sleep(5)

    if monitor.state == "SUSPENDED":
        print("Resuming COP1")
        link.resume_cop1()

    sleep(3)

    print("Disabling COP1....")
    link.disable_cop1()

    sleep(3)

    print("Initializing COP1 with set v(R)=200")
    print("  (if no CLCW is received, COP1 will be suspended in 3 seconds)")
    link.initialize_cop1("SET_VR", v_r=200)

    sleep(2)
