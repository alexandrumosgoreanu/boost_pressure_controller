from machine import Pin, ADC, PWM
from gpio_lcd import GpioLcd
import time
import wifi
import socket
import json

from ws_connection import ClientClosedError
from ws_server import WebSocketServer, WebSocketClient

# connecting to Wifi
try:
    ip = wifi.connect() 
except KeyboardInterrupt:
    print("Couldn't connect to wifi")
    machine.reset()
    
# Display Pin config
lcd = GpioLcd(rs_pin = Pin(16),
              enable_pin = Pin(17),
              d4_pin = Pin(18),
              d5_pin = Pin(19),
              d6_pin = Pin(20),
              d7_pin = Pin(21),
              num_lines = 2, num_columns = 16)

# ADC potentiometer on GPIO 28
pot = ADC(27)

# MAP sensor voltage
map = ADC(28)

# PWM on pin 14
pwm = PWM(Pin(22))
pwm.freq(50)


# reading pin analog value on 16 bits
def read_pin(pin):
    return pin.read_u16() - 320
    
# converting 16 bits ADC value to voltage
def convert_to_voltage(value):
    return value * 3.3 / 65215

# converting MAP voltage to actual measured pressure
def map_scaling(value):
    return (value - 0.030434) / 1.8478

def readSensorData(ref, map):
    refv = round(read_pin(pot) / 65215 * 1.5, 2)
    mapv = round(map_scaling(convert_to_voltage(read_pin(map))), 2)
    return refv, mapv

def printToDisplay(lcd, refv, mapv):
    lcd.putstr('Ref:' + refv + ' bar')
    lcd.move_to(0,1)
    lcd.putstr('MAP:'+ mapv + ' bar')


class Senzor(WebSocketClient):
    value = 0
    def __init__(self, conn):
        super().__init__(conn)

    def process(self, refv, mapv):
        try:
            tmp = time.localtime()
            tmp = str(tmp[3]) + ':' + str(tmp[4]) + ':' +  str(tmp[5])
            resp = {
                "date":tmp,
                "targetBoost":refv,
                "actualBoost":mapv
                }
            self.connection.write(json.dumps(resp))
            
        except ClientClosedError:
            self.connection.close()



class AppServer(WebSocketServer):
    def __init__(self):
        super().__init__("percentage.html", 10)

    def _make_client(self, conn):
        return Senzor(conn)
        
dc_minim = 5000
dc_maxim = 38000
Kp = 125000
Ki = 20000
err_sum = 0


server = AppServer()
server.start(3000)

last_time = time.ticks_us()
try:
    while True:
        refv, mapv = readSensorData(pot,map)
        printToDisplay(lcd, str(refv), str(mapv))
        
        err = mapv - refv
        output = Kp * err  + Ki * err_sum
        
        if output > dc_maxim:
            output = 65535
        if output < dc_minim:
            output = 0
        if err > 0:
            err_sum += err
        pwm.duty_u16(int(output))
        #print(output)
        
        server.process_all(refv,mapv)
        current_time = time.ticks_us()
        lcd.clear()
        
except KeyboardInterrupt:
    print("Stopped!")
    pwm.duty_u16(int(0))
    pass
server.stop()

