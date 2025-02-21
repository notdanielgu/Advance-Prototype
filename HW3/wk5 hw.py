from machine import Pin, ADC
from neopixel import NeoPixel
from time import ticks_ms, sleep_ms

print('Daniel Project#1')


btn = Pin(6, Pin.IN, Pin.PULL_UP)

analog_pin = Pin(1, Pin.IN)
adc = ADC(analog_pin)
adc.atten(ADC.ATTN_11DB)

np7 = NeoPixel(Pin(7), 30)

btn_press_time = 0
hold_threshold = 3000 
last_press_time = 0
press_count = 0  
double_press_interval = 500  
mode = "OFF_MODE" 
btn_val_last = 1 

start_delay = 80  
end_delay = 20    
delay_decrement = (start_delay - end_delay) / 30 

for i in range(30):
    np7[i] = (0, 0, 0) 
np7.write()

while True:
    btn_state = btn.value() 
    current_time = ticks_ms()  

  
    if btn_state == 0 and btn_val_last == 1:
        if current_time - last_press_time < double_press_interval:
            press_count += 1
        else:
            press_count = 1 
        last_press_time = current_time
        btn_press_time = current_time
        
    if btn_state == 1 and btn_val_last == 0:
        elapsed_time = current_time - btn_press_time

        if elapsed_time >= hold_threshold: 
            mode = "YELLOW_MODE"

        elif press_count == 2: 
            mode = "OFF_MODE"
            press_count = 0 

        elif press_count == 1 and mode == "OFF_MODE":  
            mode = "BLUE_FLOW"

    if mode == "BLUE_FLOW":  
        delay = start_delay  
        for i in range(30):
            np7[i] = (0, 0, 255)  
            np7.write()
            sleep_ms(int(delay))
            delay = max(delay - delay_decrement, end_delay)  

        mode = "ADC_MODE"  

    elif mode == "ADC_MODE":  
        analog_val = adc.read() 
        num_lights = int((analog_val / 4095) * 30) 

        for i in range(30):
            if i < num_lights:
                np7[i] = (0, 0, 255)  
            else:
                np7[i] = (0, 0, 0) 
        np7.write()

    elif mode == "YELLOW_MODE":  
        for i in range(30):
            np7[i] = (255, 255, 0)  
        np7.write()

    elif mode == "OFF_MODE":  
        for i in range(30):
            np7[i] = (0, 0, 0)  
        np7.write()

    btn_val_last = btn_state 
    sleep_ms(50) 
