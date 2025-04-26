import os, sys, io
import M5
from M5 import *
from bleuart import *
import time
from machine import ADC, Pin
from unit import VibratorUnit

# ---------- 状态变量 ----------
count_last = 1
knob_val_last = -1
knob_threshold = 10
current_mode = "GT"
in_track_mode = False
current_image_widget = None
has_shaken = False

# ---------- Encoder Δ 控制震动 ----------
vibrating = False
vibration_interval = 800
last_vibration_time = 0

# ---------- 初始化旋钮（Port C） ----------
knob = ADC(Pin(36))
knob.atten(ADC.ATTN_11DB)

# ---------- 初始化马达（Port A） ----------
vibrator_0 = VibratorUnit((33, 32))

# ---------- 初始化 M5 ----------
M5.begin()
current_image_widget = Widgets.Image("res/img/right frame.png", 0, 0, scale_x=0.2, scale_y=0.2)

# ---------- 初始化 BLE ----------
ble_client = BLEUARTClient()
print("🔄 正在连接 BLE（超时 2 秒）...")
ble_client.connect('ble-uart', timeout=2000)
print('✅ connected =', ble_client.is_connected())

# ---------- 主循环 ----------
while True:
    M5.update()

    # ✅ 旋钮判断 + 模式切换 + BLE 通知 + 图片切换
    knob_val = knob.read()
    if abs(knob_val - knob_val_last) > knob_threshold:
        print(f"本地旋钮角度值变化: {knob_val}")
        knob_val_last = knob_val

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

    # ✅ Track 模式触发一次震动
    if current_mode == "Track" and not has_shaken:
        vibrator_0.once(freq=1000, duty=30, duration=500)
        has_shaken = True

    # ✅ 本地触控判断
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

    # ✅ 接收 BLE 指令（处理多行情况）
    if ble_client.is_connected():
        data = ble_client.read()
        if data:
            try:
                msg_block = data.decode().strip()
                lines = msg_block.splitlines()
                for msg in lines:
                    print("📨 来自 Server 的消息:", msg)

                    if msg == "Vibrate":
                        print("⚡ 收到震动命令，启动周期震动")
                        vibrating = True
                        vibration_interval = 800
                        last_vibration_time = time.ticks_ms()

                    elif msg.startswith("Encoder Δ:"):
                        try:
                            delta_str = msg.replace("Encoder Δ:", "").strip()
                            delta_val = int(delta_str)
                            print(f"🎯 接收到 Encoder Δ: {delta_val}")
                            if abs(delta_val) > 3:
                                print("🛑 Δ 超过范围（绝对值 > 5），停止震动")
                                vibrating = False
                                vibration_interval = 800
                        except Exception:
                            print("⚠️ 无法解析 Δ 值:", msg)

            except Exception:
                print("⚠️ 解码失败，原始数据:", data)

    # ✅ 周期震动逻辑
    if vibrating:
        now = time.ticks_ms()

        if time.ticks_diff(now, last_vibration_time) >= vibration_interval:
            vibrator_0.once(freq=1000, duty=30, duration=500)
            last_vibration_time = now
            if vibration_interval > 200:
                vibration_interval -= 50

    time.sleep_ms(100)
