from daqhats import mcc118

hat = mcc118(0)

def read_voltage():
    return hat.a_in_read(0)