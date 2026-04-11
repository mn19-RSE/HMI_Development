import pygame
import time

screen_width = 1280
screen_height = 400

pygame.init()
screen = pygame.display.set_mode((400, 1280), pygame.FULLSCREEN)
canvas = pygame.Surface((1280, 400))  # your logical UI
pygame.mouse.set_visible(False)

canvas.fill((0, 255, 0))

rotated = pygame.transform.rotate(canvas, -90)
screen.blit(rotated, (0, 0))   # ✅ FIXED

pygame.display.flip()
time.sleep(2)

font_small = pygame.font.SysFont(None, 50)
font_large = pygame.font.SysFont(None, 100)

increment_value = 0.05



WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
GRAY = (100, 100, 100)
CYAN = (0, 255, 255)
RED = (255, 0, 0)


input_names = ["OD CUP", "LE CUP", "HE CUP", "OBJ CUP", "IMG CUP", "R45 TARGET", "R30 TARGET", "L30 TARGET"]
activeCup = 3

scale_names = ["1 nA", "10 nA", "100 nA", "1 μA", "10 μA", "100 μA", "1 mA", "10 mA"]
scale_value = 4  # binary selector

voltage = 0.0
unit = "μA"

def draw_bar(voltage):

    # Map absolute value of -10V-+10V to screen width
    bar_x = screen_width / 10
    bar_y = screen_height - 50
    bar_width = 600
    bar_height = 50

    pygame.draw.rect(canvas, GRAY, (bar_x, bar_y, bar_width, bar_height))

    # Normalize voltage
    norm = abs(voltage / 10)  # 0 to 1
    fill_width = int(norm * bar_width)

    pygame.draw.rect(canvas, DYNAMIC_COLOR, (bar_x, bar_y, fill_width, bar_height))

def draw_screen():
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
    volt_text = font_large.render(f"{voltage:+.5f} {unit}", True, DYNAMIC_COLOR)
    canvas.blit(volt_text, (250, 250))

    # Bar graph
    draw_bar(voltage)

    rotated = pygame.transform.rotate(canvas, -90)
    screen.blit(rotated, (0, 0))
    pygame.display.flip()

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # SIMULATED DATA (replace later)
    voltage += increment_value
    if voltage > 10:
        increment_value = -0.05
    if voltage < -10:
        increment_value = 0.05

    draw_screen()
    clock.tick(30)  # 30 FPS

pygame.quit()