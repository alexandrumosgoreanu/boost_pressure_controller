import network
import socket
from time import sleep

ssid = 'Andu'
password = '12131900'

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    print('Successfully connected to ' + ssid)
    print(wlan.ifconfig())
    return wlan.ifconfig()[0]
    
