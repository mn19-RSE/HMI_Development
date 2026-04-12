from daqhats import mcc118
import pygame
import time
from gpiozero import LED, Button

# daqhats init
hat = mcc118(0)

#pygame init
screen_width = 1280
screen_height = 400
pygame.init()
screen = pygame.display.set_mode((400, 1280), pygame.FULLSCREEN)
canvas = pygame.Surface((1280, 400))
pygame.mouse.set_visible(False)
canvas.fill((0, 255, 0))
rotated = pygame.transform.rotate(canvas, 90)
screen.blit(rotated, (0, 0))
pygame.display.flip()
time.sleep(2)
# pygame font sizes
font_small = pygame.font.SysFont(None, 50)
font_large = pygame.font.SysFont(None, 200)

# color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
GRAY = (100, 100, 100)
CYAN = (0, 255, 255)
RED = (255, 0, 0)

# input selections
input_names = ["OD CUP", "LE CUP", "HE CUP", "OBJ CUP", "IMG CUP", "R45 TARGET", "R30 TARGET", "L30 TARGET"]
activeCup = 0

# scale selections
scale_names = ["1 nA", "10 nA", "100 nA", "1 μA", "10 μA", "100 μA", "1 mA", "10 mA"]
scale_voltage_multipliers = [.1, 1, 10, .1, 1, 10, .1, 1]
scale_units = ["nA", "nA", "nA", "μA", "μA", "μA", "mA", "mA"]
scale_value = 0  

voltage = 0.0


def draw_bar(voltage):

    # Map absolute value of -10V-+10V to screen width
    bar_x = 0
    bar_y = screen_height - 50
    bar_width = screen_width 
    bar_height = 50

    pygame.draw.rect(canvas, GRAY, (bar_x, bar_y, bar_width, bar_height))

    # Normalize voltage
    norm = abs(voltage / 10)  # 0 to 1
    fill_width = int(norm * bar_width)

    pygame.draw.rect(canvas, DYNAMIC_COLOR, (bar_x, bar_y, fill_width, bar_height))

def draw_screen(voltage):
    global DYNAMIC_COLOR
    if voltage < 0:
        DYNAMIC_COLOR = CYAN
    elif voltage >= 0:
        DYNAMIC_COLOR = RED 
    canvas.fill(BLACK)

    # Top text
    input_text = font_small.render(f"Input: {input_names[activeCup]}", True, CYAN)
    range_text = font_small.render(f"Range: Max Value = ±{scale_names[scale_value]}", True, CYAN)

    canvas.blit(input_text, (20, 20))
    canvas.blit(range_text, (500, 20))

    # Big voltage display
    volt_text = font_large.render(f"{voltage:+.5f} {scale_units[scale_value]}", True, DYNAMIC_COLOR)
    canvas.blit(volt_text, (450, 200))

    # Bar graph
    draw_bar(voltage)

    rotated = pygame.transform.rotate(canvas, 90)
    screen.blit(rotated, (0, 0))
    pygame.display.flip()

def read_voltage():
    return hat.a_in_read(0)




# Main loop
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    voltage = read_voltage() * scale_voltage_multipliers[scale_value]
    if abs(voltage) < .0001:
        voltage = 0
    draw_screen(voltage)
    clock.tick(60)  # 60 FPS

pygame.quit()

