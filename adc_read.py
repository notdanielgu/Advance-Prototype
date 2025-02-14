from machine import Pin, ADC
from time import *


# configue pin 1 as input:
analog_pin = Pin(1, Pin.IN)

# configure ADC on an input pin:
adc = ADC(analog_pin)

# configure the ADC sensitiviity:
adc.atten(ADC.ATTN_11DB)

while True:
    analog_val = adc.read()
    # print(analog_val)
    analog_val_8bit = int(analog_val/16)
    print(analog_val_8bit)
    sleep_ms(100)