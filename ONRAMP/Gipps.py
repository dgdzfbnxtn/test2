import numpy as np
import math
from ctypes import *

class Gipps(object):
    def __init__(self):
        self.L = 3

    def carfollowing(self,speed, leader,maxacc = 3,maxdec = -3,pre_maxdec = -3,TimeStep = 0.1,v_max = 120,T = 0.7,length = 6):

        maxacc = 3
        maxdec = -3
        pre_maxdec = -3
        TimeStep = 0.1
        v_max = 120
        T = 0.7
        length = 6
        # v_free = min(Car.cur_lane.v_max,Car.speed + Car.maxacc)
        v_free = speed + 2.5 * maxacc * TimeStep * (1 - speed / v_max * math.sqrt(0.025 + speed / v_max))
        if leader:
            D,pre_speed = leader
            x = maxdec ** 2 * T ** 2 / 4 - 2 * ( - D + length  + self.L +
                                                        speed * T / 2) + pre_speed ** 2 * maxdec / maxdec
            v_t = min(-maxdec * T / 2 + math.sqrt(abs(x)),v_free)
        # print("v_free",v_free,"v",v_t,"sqrt",x)
        else:
            v_t = v_free
        acc = min(max((v_t - speed) / T, -maxdec), maxacc)

        return acc


