import serial

ser = serial.Serial(
    port="/dev/serial0",
    baudrate=500000,
    timeout=0
)

def read_adc():
    """Read one valid ADC sample from UART."""
    while ser.in_waiting >= 3:
        byte = ser.read(1)

        if byte[0] == 0xA5:  # sync
            data = ser.read(2)
            if len(data) == 2:
                lsb = data[0]
                msb = data[1]
                return (msb << 8) | lsb

    return None