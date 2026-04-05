import pygame
import time


pygame.init()
screen = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)


font_small = pygame.font.SysFont("Bahnschrift", 50)
font_large = pygame.font.SysFont("Bahnschrift", 100)

increment_value = 0.05

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
GRAY = (100, 100, 100)
CYAN = (0, 255, 255)

# Example dynamic values (replace later)
input_names = ["OD CUP", "LE CUP", "HE CUP", "OBJ CUP", "IMG CUP", "R45 TARGET", "R30 TARGET", "L30 TARGET"]
activeCup = 3

scale_names = ["1 nA", "10 nA", "100 nA", "1 μA", "10 μA", "100 μA", "1 mA", "10 mA"]
scale_value = 4  # binary selector

voltage = 0.0
unit = "μA"

def draw_bar(voltage):
    # Map absolute value of -10V-+10V to screen width
    bar_x = 100
    bar_y = 400
    bar_width = 600
    bar_height = 50

    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))

    # Normalize voltage
    norm = abs(voltage / 10)  # 0 to 1
    fill_width = int(norm * bar_width)

    pygame.draw.rect(screen, CYAN, (bar_x, bar_y, fill_width, bar_height))

def draw_screen():
    screen.fill(BLACK)

    # Top text
    input_text = font_small.render(f"Input: {input_names[activeCup]}", True, CYAN)
    range_text = font_small.render(f"Range: Max Value = ±{scale_names[scale_value]}", True, CYAN)

    screen.blit(input_text, (20, 20))
    screen.blit(range_text, (500, 20))

    # Big voltage display
    volt_text = font_large.render(f"{voltage:+.5f} {unit}", True, CYAN)
    screen.blit(volt_text, (250, 250))

    # Bar graph
    draw_bar(voltage)

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