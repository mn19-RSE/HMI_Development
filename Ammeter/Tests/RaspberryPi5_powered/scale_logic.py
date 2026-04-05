from gpiozero import LED, Button
from signal import pause

# Output pins (LSB to MSB)
pins = [LED(17), LED(27), LED(22)]

# Input buttons (pull_up=True assumes button to GND)
btn_up = Button(5, pull_up=True, bounce_time=0.1)
btn_down = Button(6, pull_up=True, bounce_time=0.1)

# Current value (0–7)
value = 0

def update_outputs():
    """Update GPIO outputs to match current value."""
    for i in range(3):
        if (value >> i) & 1:
            pins[i].on()
        else:
            pins[i].off()
    print(f"Value: {value} -> {value:03b}")

def increment():
    global value
    value = (value + 1) % 8  # Wrap 7 → 0
    update_outputs()

def decrement():
    global value
    value = (value - 1) % 8  # Wrap 0 → 7
    update_outputs()

# Attach button events
btn_up.when_pressed = increment
btn_down.when_pressed = decrement

# Initialize outputs
update_outputs()

print("Ready. Press buttons to change value.")
pause()