from daqhats import OptionFlags, mcc118
import numpy as np
import pygame
import time
from gpiozero import LED, Button
import socket
import os
import json 
from collections import deque
import SM16relind


# pygame init
screen_width = 1280
screen_height = 400
pygame.init()
screen = pygame.display.set_mode((400, 1280), pygame.FULLSCREEN)
canvas = pygame.Surface((1280, 400))
pygame.mouse.set_visible(False)
# canvas.fill((0, 255, 0))
rotated = pygame.transform.rotate(canvas, 90)
screen.blit(rotated, (0, 0))
pygame.display.flip()

# pygame font sizes
font_small = pygame.font.SysFont(None, 50)
font_large = pygame.font.SysFont(None, 150)
# static image load
vdg_logo = pygame.image.load("HMI_Development/Ammeter/Code_builds/Python_Ammeter/vdg.png").convert_alpha()

# daqhats init
hat = mcc118(0)
ema_voltage = 0.0
EMA_ALPHA = 0.15  # 0.1 = very smooth, 0.3 = more responsive

# Start continuous hardware scan at 1200 Hz on channel 0
SCAN_RATE = 1200.0
BUFFER_SIZE = 12000
hat.a_in_scan_start(1 << 0, BUFFER_SIZE, SCAN_RATE, OptionFlags.CONTINUOUS)

# relay board init
for attempt in range(10):
    try:
         rel0 = SM16relind.SM16relind(0) # 1-12 shields
         rel1 = SM16relind.SM16relind(1) # 13-24
         break
    except Exception as e:
         print(f"relay board init failed (attmpt {attempt + 1}/10): {e}")
         time.sleep(10)
else:
    raise RuntimeError("Could not initialize sm16 relay boards after 10 attempts")



# oversample definitions
SAMPLE_COUNT = 8  # adjust (8–32 is typical)
samples = deque(maxlen=SAMPLE_COUNT)

# network variables
UDP_IP = "192.168.42.15" # Change to 42.15 for final implementation
UDP_PORT = 60000 # destination port
LISTEN_PORT = 60000 # port to listen on 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", LISTEN_PORT))
sock.setblocking(False) # needed for listening to not pause script

# gpio init
# scale output pins (LSB - MSB)
pins = [LED(21), LED(20), LED(19)] # tested, seems correct 21, 20, 19
# scale button pins
btn_up = Button(4, pull_up=True, bounce_time=0.05)
btn_down = Button(27, pull_up=True, bounce_time=0.05) 

# input button pins
cup_btn_up = Button(23, pull_up=True, bounce_time=0.05)
cup_btn_down = Button(22, pull_up=True, bounce_time=0.05)

# color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PURPLE = (100, 0, 255)
PINK = (255, 0, 255)

# input selections
input_names = ["OD CUP", "LE CUP", "HE CUP", "OBJ CUP", "IMG CUP", "6", "7", "8", "9", "10", "11", "12"] 
input_xlocations = [750, 610, 360, 290, 245, 10000, 10000, 10000, 10000, 10000, 10000, 10000]
input_ylocations = [127, 127, 127, 127, 170, 10000, 10000, 10000, 10000, 10000, 10000, 10000]

activeCup = 1 # defaults to LE cup when power cycled
input_key = "ch_lecup_ival"
previous_cup = 0

# scale selections
'''
scale_names = ["100 pA", "1 nA", "10 nA", "100 nA", "1 μA", "10 μA", "100 μA", "1 mA"]
scale_voltage_multipliers = [10, .1, 1, 10, .1, 1, 10, .1]
scale_units = ["pA", "nA", "nA", "nA", "μA", "μA", "μA", "mA"]
scale_value = 2
'''
# testing truncating scales that dont work or are not needed
# scale selections
scale_names = ["10 nA", "100 nA", "1 μA", "10 μA", "30 μA"]
# multiplier applied to the MCC118 voltage
scale_voltage_multipliers = [1, 10, .1, 1, 10]
# display units
scale_units = ["nA", "nA", "μA", "μA", "μA"]
# maximum display value for each range
scale_max_values = [10, 100, 1, 10, 30]
scale_value = 3 # defualts to 10uA scale when power cycled

# daq read vairables
voltage = 0.0
scaled_voltage = 0.0

# screen mirroring variables
last_save_time = 0
SAVE_INTERVAL = 0.1  # 10 FPS

# UDP send rate
last_udp_time = 0
UDP_INTERVAL = 1  # 1 Hz 

# text display rate
last_text_voltage = 0.0
last_volt_time = 0
VOLT_INTERVAL = 1 # 1 Hz

# zero clamp width
DEADBAND = 0.1


def write_board_safe(board, mask, label, retries=5):
    for attempt in range(retries):
        try:
            board.set_all(mask)
            return True
        except Exception as e:
            print(f"I2C write failed on {label} (attempt {attempt + 1}/{retries}): {e}", flush=True)
            time.sleep(0.05)
    return False


def set_cup(activeCup):
    global previous_cup, input_key
    if activeCup == previous_cup:
        return

    # Disconnect ALL conductors from the amplifier first (zero overlap between cups, no amp-to-shield short)
    if not write_board_safe(rel1, 0x0000, "rel1 open all conductors"):
        return
    time.sleep(0.02)  # Wait 20ms for mechanical reed relay to fully release

    # Connect ALL 12 conductors to their shields (no floating conductors)
    if not write_board_safe(rel0, 0x0FFF, "rel0 close all shields"):
        return
    time.sleep(0.02)  # Wait 20ms for shield reed relay to close

    # Disconnect ONLY the desired cup from its shield
    shield_mask = 0x0FFF & ~(1 << activeCup)
    if not write_board_safe(rel0, shield_mask, f"rel0 open shield {activeCup + 1}"):
        return
    time.sleep(0.02)  # Wait 20ms for shield reed relay to release before connecting amp

    # Connect ONLY the desired cup to the amplifier
    cond_mask = (1 << activeCup)
    if not write_board_safe(rel1, cond_mask, f"rel1 close conductor {activeCup + 1}"):
        # Fail-safe: re-ground target cup to shield so it never remains floating
        write_board_safe(rel0, 0x0FFF, "rel0 fail-safe ground all")
        return

    cup_keys = [
        "ch_odcup_ival", "ch_lecup_ival", "ch_hecup_ival", "ch_objcup_ival",
        "ch_imgcup_ival", "ch_6cup_ival", "ch_7cup_ival", "ch_8cup_ival",
        "ch_9cup_ival", "ch_10cup_ival", "ch_11cup_ival", "ch_12cup_ival"
    ]
    input_key = cup_keys[activeCup]
    previous_cup = activeCup



def increment_cup():
    global activeCup
    activeCup = (activeCup + 1) % 12
    
def decrement_cup():
    global activeCup
    activeCup = (activeCup - 1) % 12
    
def draw_active_cup():
    pygame.draw.circle(canvas, PINK, (input_xlocations[activeCup], input_ylocations[activeCup]), 10, 10)


def draw_bar(voltage):
    # Map absolute value of -10V to +10V to screen width
    bar_x = 0
    bar_height = 100
    bar_y = screen_height - bar_height
    bar_width = screen_width 
    
    pygame.draw.rect(canvas, GRAY, (bar_x, bar_y, bar_width, bar_height))

    # Normalize voltage
    norm = abs(voltage / 10)  # 0 to 1
    if scale_value == 4:
        norm  = norm * 3.333333
    fill_width = int(norm * bar_width)
    pygame.draw.rect(canvas, DYNAMIC_COLOR, (bar_x, bar_y, fill_width, bar_height))
    
    pygame.draw.rect(canvas, WHITE, (bar_x, bar_y, 2, bar_height))
    pygame.draw.rect(canvas, WHITE, (bar_x + (bar_width / 2), bar_y, 2, bar_height))
    pygame.draw.rect(canvas, WHITE, (bar_x + (bar_width / 4), bar_y, 2, bar_height))
    pygame.draw.rect(canvas, WHITE, (bar_x + (3 * bar_width / 4), bar_y, 2, bar_height))
    pygame.draw.rect(canvas, WHITE, (bar_x + bar_width - 2, bar_y, 2, bar_height))

    pygame.draw.rect(canvas, WHITE, (bar_x + (bar_width / 8), bar_y, 2, bar_height / 2))
    pygame.draw.rect(canvas, WHITE, (bar_x + (3 * bar_width / 8), bar_y, 2, bar_height / 2))
    pygame.draw.rect(canvas, WHITE, (bar_x + (5 * bar_width / 8), bar_y, 2, bar_height / 2))
    pygame.draw.rect(canvas, WHITE, (bar_x + (7 * bar_width / 8), bar_y, 2, bar_height / 2))

    pygame.draw.rect(canvas, WHITE, (bar_x + (bar_width / 16), bar_y, 2, bar_height / 3))
    pygame.draw.rect(canvas, WHITE, (bar_x + (3 * bar_width / 16), bar_y, 2, bar_height / 3))
    pygame.draw.rect(canvas, WHITE, (bar_x + (5 * bar_width / 16), bar_y, 2, bar_height / 3))
    pygame.draw.rect(canvas, WHITE, (bar_x + (7 * bar_width / 16), bar_y, 2, bar_height / 3))
    pygame.draw.rect(canvas, WHITE, (bar_x + (9 * bar_width / 16), bar_y, 2, bar_height / 3))
    pygame.draw.rect(canvas, WHITE, (bar_x + (11 * bar_width / 16), bar_y, 2, bar_height / 3))
    pygame.draw.rect(canvas, WHITE, (bar_x + (13 * bar_width / 16), bar_y, 2, bar_height / 3))
    pygame.draw.rect(canvas, WHITE, (bar_x + (15 * bar_width / 16), bar_y, 2, bar_height / 3))
    
    #bar graph tick mark
    pygame.draw.rect(canvas, RED, (fill_width - 4, bar_y, 4, bar_height))

def draw_screen(voltage, scaled_voltage):
    global last_volt_time
    global last_text_voltage
    global DYNAMIC_COLOR
    if voltage < -0.05:
        DYNAMIC_COLOR = BLUE
    elif voltage >= 0.05:
        DYNAMIC_COLOR = GREEN
    else: 
        DYNAMIC_COLOR = CYAN
    canvas.fill(BLACK)

    # Top text
    if activeCup == len(input_names):
        INPUT_COLOR = RED
    else:
        INPUT_COLOR = CYAN
    input_text = font_small.render(f"Input: {input_names[activeCup]}", True, INPUT_COLOR)
    canvas.blit(input_text, (20, 20))

    range_text = font_small.render(f"Range: Max Value = ±{scale_names[scale_value]}", True, CYAN)
    rect = range_text.get_rect()
    rect.topright = (1260, 20)
    canvas.blit(range_text, rect)
    
    # vdg logo draw
    canvas.blit(vdg_logo, (175, 87))

    if activeCup < 5:
        draw_active_cup()

    now = time.time()
    if now - last_volt_time > VOLT_INTERVAL:
        last_volt_time = now
        last_text_voltage = scaled_voltage

    # max value for selected range
    max_value = scale_max_values[scale_value]

    # display normal value while within range
    if abs(last_text_voltage) <= max_value:
        volt_text = font_large.render(f"{last_text_voltage:+.5f} {scale_units[scale_value]}", True, DYNAMIC_COLOR)
        rect = volt_text.get_rect()
        rect.topright = (1260, 200)
        canvas.blit(volt_text, rect)

    # display OL when over range limit
    else:
        DYNAMIC_COLOR = RED
        over_limit = font_large.render("OL", True, RED)
        rect = over_limit.get_rect()
        rect.topright = (1260, 200)
        canvas.blit(over_limit, rect)
         
    # bar graph
    draw_bar(voltage)
    rotated = pygame.transform.rotate(canvas, 90)
    screen.blit(rotated, (0, 0))
    pygame.display.flip()

def read_voltage_oversampled():
    # Drain all samples collected by the MCC 118 hardware since the last frame
    read_result = hat.a_in_scan_read(-1, 0.0)
    if len(read_result.data) > 0:
        return float(np.mean(read_result.data))
    return ema_voltage  # Fallback if a frame runs faster than 1 sample period


def apply_ema(new_value):
    # smoothing
    global ema_voltage
    ema_voltage = (EMA_ALPHA * new_value) + ((1 - EMA_ALPHA) * ema_voltage)
    return ema_voltage

# set scale output decimal to binary 
def update_outputs():
    if scale_value == 0:
        pins[2].off()
        pins[1].on()
        pins[0].off()
    if scale_value == 1:
        pins[2].off()
        pins[1].on()
        pins[0].on()
    if scale_value == 2:
        pins[2].on()
        pins[1].off()
        pins[0].off()
    if scale_value == 3:
        pins[2].on()
        pins[1].off()
        pins[0].on()
    if scale_value == 4:
        pins[2].on()
        pins[1].on()
        pins[0].off()

def increment():
    global scale_value
    scale_value = (scale_value + 1) % 5
    update_outputs()

def decrement():
    global scale_value
    scale_value = (scale_value - 1) % 5
    update_outputs()

def send_all_data():
    try:
        value_nA = convert_to_nA(scaled_voltage, scale_units[scale_value])
        msg = {
           # "ts": time.time(),
            input_key: float(value_nA)
        }
        msg_bytes = json.dumps(msg).encode('utf-8')
        sock.sendto(msg_bytes, (UDP_IP, UDP_PORT))
    except Exception as e:
        print("UDP send error:", e)

# converts all values to nA for easier graphing
def convert_to_nA(value, unit):
    if unit == "μA":
        return value * 1e3
    else:
        return value

def handle_touch_cups(x, y):
    global activeCup

    for i in range(5):
        cx = input_xlocations[i]
        cy = input_ylocations[i]

        radius = 35
        if (x - cx)**2 + (y - cy)**2 <= radius**2:
            activeCup = i
            print(f"Selected cup: {input_names[i]}", flush=True)
            return


# Main loop
running = True
clock = pygame.time.Clock()
btn_up.when_pressed = increment
btn_down.when_pressed = decrement
cup_btn_up.when_pressed = increment_cup
cup_btn_down.when_pressed = decrement_cup
update_outputs() # run once to fix startup bug
while running:
    for event in pygame.event.get():
        # print("EVENT RECEIVED:", event, flush=True)
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.FINGERDOWN:
            x = int((1.0 - event.y) * screen_width)
            y = int(event.x * screen_height)

            # print(f"canvas touch: ({x}, {y})", flush=True)
            handle_touch_cups(x, y)




    # set cup
    set_cup(activeCup)     

    # oversampling
    raw = read_voltage_oversampled() # default is 4

    # rolling average
    samples.append(raw)
    avg_voltage = sum(samples) / len(samples)

    # Exponential moving average 
    voltage = apply_ema(avg_voltage)

    # less abrupt zero clamp
    if abs(voltage) < DEADBAND:
        voltage *= 0.2

    scaled_voltage = voltage * scale_voltage_multipliers[scale_value]

    draw_screen(voltage, scaled_voltage)

    # UDP packet send at reduced rate
    now = time.time()
    if now - last_udp_time > UDP_INTERVAL:
        send_all_data()
        last_udp_time = now

    try:
        data, addr = sock.recvfrom(1024)
        cmd = data.decode().strip()
        if cmd == "UP":
            increment()
        elif cmd == "DOWN":
            decrement()
        elif cmd == "CUPUP":
            increment_cup()
        elif cmd == "CUPDOWN":
            decrement_cup()
    except BlockingIOError:
        pass

    # saving a frame at a set interval to mirror on web
    now = time.time()
    if now - last_save_time > SAVE_INTERVAL:
        pygame.image.save(canvas, "/tmp/frame_tmp.jpg")
        os.replace("/tmp/frame_tmp.jpg", "/tmp/frame.jpg") # flicker reducing swap
        last_save_time = now

    clock.tick(60)  # FPS
    
hat.a_in_scan_stop()
hat.a_in_scan_cleanup()
pygame.quit()
