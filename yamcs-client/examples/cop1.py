from __future__ import print_function

from time import sleep
from pprint import pprint

from yamcs.client import YamcsClient

global cop1_status

def callback(status):
    global cop1_status
    print('In callback COP1 status: ', status)
    cop1_status = status


if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    
    cop1_config = client.get_cop1_config('opsim', 'UDP_FRAME_OUT.tc')
    print('COP1 congiguration: ', cop1_config)
    
    print("Changing COP1 configuration")
    cop1_config.t1 = cop1_config.t1 + 100
    #cop1_config.timeout_type = 'SUSPEND'
    cop1_config.tx_limit = cop1_config.tx_limit+1
    client.set_cop1_config('opsim', 'UDP_FRAME_OUT.tc', cop1_config)
    
    cop1_config = client.get_cop1_config('opsim', 'UDP_FRAME_OUT.tc')
    print('New COP1 congiguration: ', cop1_config)
    
    
    cop1_status = client.get_cop1_status('opsim', 'UDP_FRAME_OUT.tc')
    print('Initial COP1 status from get_cop1_status(): ', cop1_status) 
    
    
    cop1 = client.create_cop1_subscription('opsim', 'UDP_FRAME_OUT.tc', callback)
    print("COP1 status subscribed.")
 
    print("disabling COP1....")
    client.disable_cop1('opsim', 'UDP_FRAME_OUT.tc')
    
    
    sleep(3)    
    print("initializing COP1 with CLCW_CHECK (if no CLCW is received, COP1 will be suspended in 3 seconds)")
    client.initialize_cop1('opsim', 'UDP_FRAME_OUT.tc', type='WITH_CLCW_CHECK', clcw_wait_timeout=3000)
           
    sleep(5)
    
    if cop1_status.state == 'SUSPENDED':
        print("resuming COP1 ")
        client.resume_cop1('opsim', 'UDP_FRAME_OUT.tc')
    
    sleep(3)
    
    
    print("unsubscribing the link")
    cop1.remove('opsim', 'UDP_FRAME_OUT.tc')
    
    
    sleep(1)
    print("subscribing again the link")
    cop1.add('opsim', 'UDP_FRAME_OUT.tc')
   
    sleep(2)
