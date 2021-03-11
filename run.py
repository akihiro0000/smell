import spidev
import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
from datetime import datetime

threshold = 500

mqtt_client = mqtt.Client()
mqtt_client.connect("fluent-bit",1883, 60)

GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)

spi = spidev.SpiDev()

spi.open(0,0)

spi.max_speed_hz=1000000

spi.bits_per_word=8

dummy = 0xff
start = 0x47
sgl = 0x20

ch0 = 0x00

msbf = 0x08

def measure(ch):
    ad = spi.xfer2( [ (start + sgl + ch + msbf), dummy ] )
    val = ((ad[0] & 0x03) << 8) + ad[1]
    return val

try:
    while 1:
        time.sleep(0.237)

        GPIO.output(22,True)
        time.sleep(0.003)

        ch0_val = measure(ch0)
        Val = 1023 - ch0_val
        time.sleep(0.002)
        GPIO.output(22,False)
        
        GPIO.output(17,True)
        time.sleep(0.008)
        GPIO.output(17,False)

        tim = '"timestamp":"'+datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')+'"'
        Val = '"' + "value" + '"' + ":" + '"' + str(Val) + '"'
        mylist = [tim,Val]
        mystr = '{' + ','.join(map(str,mylist))+'}'
        print(mystr)
        mqtt_client.publish("{}/{}".format("/demo",'car_count'), mystr)


except KeyboardInterrupt:
    pass

spi.close()
mqtt_client.disconnect()
