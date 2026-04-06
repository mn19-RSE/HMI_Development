from daqhats import mcc118, HatIDs
from daqhats_utils import select_hat_device

# initialize once
address = select_hat_device(HatIDs.MCC_118)
hat = mcc118(address)

def read_voltage():
    return hat.a_in_read(0)