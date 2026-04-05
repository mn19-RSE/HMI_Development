import pygame
import time


pygame.init()
screen = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)


font_small = pygame.font.SysFont("Arial", 30)
font_large = pygame.font.SysFont("Arial", 80)


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
GRAY = (100, 100, 100)

# Example dynamic values (replace later)
input_names = ["OD CUP", "LE CUP", "HE CUP", "OBJ CUP", "IMG CUP", "R45 TARGET", "R30 TARGET", "L30 TARGET"]
activeCup = 0
value = 3  # binary selector
voltage = 0.0
unit = " uA"

def draw_bar(voltage):
    # Map absolute value of -10V-+10V to screen width
    bar_x = 100
    bar_y = 350
    bar_width = 600
    bar_height = 20

    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))

    # Normalize voltage
    norm = (abs(voltage)) / 10  # 0 to 1
    fill_width = int(norm * bar_width)

    pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_width, bar_height))

def draw_screen():
    screen.fill(BLACK)

    # Top text
    input_text = font_small.render(f"Input: {input_names[activeCup]}", True, WHITE)
    range_text = font_small.render(f"Range: {value} ({value:03b})", True, WHITE)

    screen.blit(input_text, (20, 20))
    screen.blit(range_text, (500, 20))

    # Big voltage display
    volt_text = font_large.render(f"{voltage:+.3f} {unit}", True, WHITE)
    screen.blit(volt_text, (200, 150))

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

    # ---- SIMULATED DATA (replace later) ----
    voltage += 0.05
    if voltage > 10:
        voltage = -10
    # ---------------------------------------

    draw_screen()
    clock.tick(30)  # 30 FPS

pygame.quit()