# Daniel's Final Documentation
## Introduction

The original idea for my project was to create an interactive steering wheel item that not only had the functionality of being able to interact normally, but also provided some track assistance. This product was designed for Aston Martin, so I'm also trying to incorporate the design of Aston Martin's existing steering wheel, but really this is difficult.

I'm hoping this steering wheel will give some track beginners the courage to hit the track and help them become better acquainted with this car in their hands!

![Sketch](final-concept-sketches.jpg)  

## Implementation  

### State Diagram
![Sketch](State-Diagram.jpg)  

### Hardware
- [M5Stack Core2](https://shop.m5stack.com/products/m5stack-core2-esp32-iot-development-kit-for-aws-iot-edukit). This one is the main core, and its function is to connect the computer to other components, and to display some basic UI on the steering wheel, providing a connection to the dashboard.

- [Button Unit](https://shop.m5stack.com/products/mechanical-key-button-unit).This is used as the car's starter button

- [Button Unit](https://shop.m5stack.com/products/encoder-unit). This is used to check how much the steering wheel has actually turned

- [Vibration Unit](https://shop.m5stack.com/products/vibration-motor-unit). This is used to alert the user to enter track mode and to give him/her a turn alert.

- [Angle Unit](https://shop.m5stack.com/products/angle-unit). This is used to switch modes

### Wire Diagram
![Sketch](Wire-Diagram.jpg)  


### Firmware
So I used two separate pieces of code to control each of the two cores and have them communicate with each other via the bluetooth code as follows
Clint script
```
ble_client = BLEUARTClient()
print("🔄 正在连接 BLE（超时 2 秒）...")
ble_client.connect('ble-uart', timeout=2000)
print('✅ connected =', ble_client.is_connected())
```
Server script
```
ble_server = BLEUARTServer(name='ble-uart')
print("✅ BLE Server Started")
```

On the Clint side, I split the output of the angle unit into three segments, each representing the corresponding mode.
```
if knob_val <= 1365 and current_mode != "GT":
        current_mode = "GT"
        in_track_mode = False
        has_shaken = False
        print("GT")
        if ble_client.is_connected():
            ble_client.write("mode: GT\n")
        if current_image_widget:
            del current_image_widget
        current_image_widget = Widgets.Image("res/img/right frame.png", 0, 0, scale_x=0.2, scale_y=0.2)

    elif 1366 <= knob_val <= 2730 and current_mode != "Sport":
        current_mode = "Sport"
        in_track_mode = False
        has_shaken = False
        print("Sport")
        if ble_client.is_connected():
            ble_client.write("mode: Sport\n")
        if current_image_widget:
            del current_image_widget
        current_image_widget = Widgets.Image("res/img/right frame.png", 0, 0, scale_x=0.2, scale_y=0.2)

    elif knob_val > 2730 and current_mode != "Track":
        current_mode = "Track"
        in_track_mode = True
        has_shaken = False
        print("Track")
        if ble_client.is_connected():
            ble_client.write("mode: Track\n")
        if current_image_widget:
            del current_image_widget
        current_image_widget = Widgets.Image("res/img/hardness.png", 0, 0, scale_x=0.2, scale_y=0.2)
```

For this section I divided the screen into nine sections, each representing an output, and also made two modes so that the screen could change touch areas with the modes
```
count = M5.Touch.getCount()
    if count > 0:
        x = M5.Touch.getX()
        y = M5.Touch.getY()
        if in_track_mode:
            if 60 <= x <= 260 and 40 <= y <= 200:
                print("Shake")
        else:
            if 0 <= x <= 106 and 0 <= y <= 80:
                print("Decrease Volume")
            elif 107 <= x <= 213 and 0 <= y <= 80:
                print("Up")
            elif 214 <= x <= 320 and 0 <= y <= 80:
                print("Increase Volume")
            elif 0 <= x <= 106 and 81 <= y <= 160:
                print("Left")
            elif 107 <= x <= 213 and 81 <= y <= 160:
                print("Enter")
            elif 214 <= x <= 320 and 81 <= y <= 160:
                print("Right")
            elif 107 <= x <= 213 and 161 <= y <= 240:
                print("Down")
    else:
        if count_last != count:
            print("No touch")
            count_last = count
```

This section allows the Clint side to receive information from the server side and respond accordingly.
```
    if ble_client.is_connected():
        data = ble_client.read()
        if data:
            try:
                msg_block = data.decode().strip()
                lines = msg_block.splitlines()
                for msg in lines:
                    print("来自 Server 的消息:", msg)

                    if msg == "Vibrate":
                        print("⚡ 收到震动命令，启动周期震动")
                        vibrating = True
                        vibration_interval = 800
                        last_vibration_time = time.ticks_ms()

                    elif msg.startswith("Encoder Δ:"):
                        try:
                            delta_str = msg.replace("Encoder Δ:", "").strip()
                            delta_val = int(delta_str)
                            print(f"接收到 Encoder Δ: {delta_val}")
                            if abs(delta_val) > 3:
                                print("Δ 超过范围（绝对值 > 5），停止震动")
                                vibrating = False
                                vibration_interval = 800
```

So now I'm going to talk about the script on the server side.
First write a simple piece of code to make the button's light follow the state of the switch
```
button_now = button.value()
    if button_last_pressed == 1 and button_now == 0:
        if button_state == 0:
            button_state = 1
            print("start")
            ble_server.write("start\n")
            key_0.set_color(0x00ff00)
        else:
            button_state = 0
            print("close")
            ble_server.write("close\n")
            key_0.set_color(0x000000)
    button_last_pressed = button_now
```

This section lets the server receive information from the Clint side to change the color of the button
```
 data = ble_server.read()
    if data:
        try:
            msg = data.decode().strip()
            print("来自 Client:", msg)

            if msg == "mode: GT":
                key_0.set_color(0x00ff00)
                in_track_mode = False
                if current_image_widget:
                    del current_image_widget
                current_image_widget = Widgets.Image("res/img/Frame 156.png", 0, 0, scale_x=0.2, scale_y=0.2)

            elif msg == "mode: Sport":
                key_0.set_color(0xff6600)
                in_track_mode = False
                if current_image_widget:
                    del current_image_widget
                current_image_widget = Widgets.Image("res/img/Frame 156.png", 0, 0, scale_x=0.2, scale_y=0.2)

            elif msg == "mode: Track":
                key_0.set_color(0xcc0000)
                in_track_mode = True
                if current_image_widget:
                    del current_image_widget
                current_image_widget = Widgets.Image("res/img/switch.png", 0, 0, scale_x=0.2, scale_y=0.2)
```

Similarly, the server is also given a touch area to output different information depending on the area
```
 count = M5.Touch.getCount()
    if count > 0:
        x = M5.Touch.getX()
        y = M5.Touch.getY()

            if 60 <= x <= 260 and 40 <= y <= 120:
                print("Vibrate")
                ble_server.write("Vibrate\n")
            elif 60 <= x <= 260 and 121 <= y <= 200:
                print("HUD")
                ble_server.write("HUD\n")
        else:
            if 107 <= x <= 213 and 0 <= y <= 80:
                print("Speed Up")
                ble_server.write("Speed Up\n")
            elif 0 <= x <= 106 and 81 <= y <= 160:
                print("Cruise control")
                ble_server.write("Cruise control\n")
            elif 214 <= x <= 320 and 81 <= y <= 160:
                print("Road detection")
                ble_server.write("Road detection\n")
            elif 107 <= x <= 213 and 161 <= y <= 240:
                print("Speed Down")
                ble_server.write("Speed Down\n")
    else:
        if count_last != count:
            print("No touch")
            count_last = count
```

























