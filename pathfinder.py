import numpy as np
import params as p

def get_theta(pos1, pos2):
    return -np.degrees(np.arctan((pos1[0]-pos2[0]) / (pos1[1]-pos2[1])))



def get_offset(theta, offset_limit =75):
    offset = int((theta / (1024 / 300)) * p.TURNING_POWER)
    # offset = int(theta ** p.TURNING_POWER / ((1024/300) * (p.TURNING_POWER ** 2)))
    if offset <= -offset_limit:
        return 0
    if offset >= offset_limit:
        return offset_limit * 2
    return offset +offset_limit