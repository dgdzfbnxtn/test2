
import traci
import math
import os
import sys
import time
import optparse
import random
from sumolib import checkBinary
import numpy as np
from Onehot2numpy import *
from Gipps import *

class Vehicle(object):
    def __init__(self, veh_id, lanes_num):
        self.veh_id = veh_id
        self.vehspeed_max = 55
        self.lane_index = None  # 所在车道索引
        self.desired_lane = None  # 期望车道
        self.int_phase = None  # 相位
        self.remain_duration = None  # 转到下一相位需要的时间
        self.speed = None
        self.dist_to_light = None
        self.lanespeed = None

        self.lanes_num = lanes_num

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


class SumoEnv(object):

    def __init__(self):

        self.min_length = 10
        self.lane_divide = np.arange(0, 200, self.min_length)
        self.state_size = len(self.lane_divide) * 11# + 2
        self.action_size = 2**258
        self.Onehot2numpy = Onehot2numpy(260)
        self.Gipps = Gipps()
        self.edgelist = {'gneE4':3, 'gneE5':4, 'gneE6':3, 'gneE7':1}
        self.lanelist = ["gneE4_0","gneE4_1","gneE4_2","gneE5_0","gneE5_1","gneE5_2","gneE5_3","gneE6_0","gneE6_1","gneE6_2","gneE7_0"]
        self.action_choose = {"gneE4_0":[0,1,[1]],"gneE4_1":[7,2,[0,2]],"gneE4_2":[1,1,[1]], "gneE5_0":[4,1,[1]],"gneE5_1":[5,1,[2]],"gneE5_2":[11,2,[1,3]],"gneE5_3":[6,1,[2]],
            "gneE6_0":[2,1,[1]],"gneE6_1":[9,2,[0,2]],"gneE6_2":[3,1,[1]]} #

        if 'SUMO_HOME' in os.environ:
            tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
            sys.path.append(tools)
        else:
            sys.exit("please declare environment variable 'SUMO_HOME'")

        # if_show_gui = False

        options = get_options()
        if options.nogui:
            self.sumoBinary = checkBinary('sumo')
        else:
            self.sumoBinary = checkBinary('sumo-gui')


    def set_lanechangemode(self, veh_id):
        """关掉sumo的换道模型"""
        traci.vehicle.setLaneChangeMode(veh_id,  0)

    def set_speedmode(self, veh_id):
        "关掉sumo的速度模型"
        traci.vehicle.setSpeedMode(veh_id, 00000)


    def reset(self):

        self.sumocfgfile = "map/onramp.sumocfg"

        traci.start([self.sumoBinary, "-c", self.sumocfgfile, "--tripinfo-output",
                 "tripinfo.xml"])
        vehicle_density = self.get_state()
        return vehicle_density

    def get_state(self):
        vehicle_density = []
        for edgeid in self.edgelist:
            lanenumber = traci.edge.getLaneNumber(edgeid)
            # print(traci.edge.len)
            for ln in range(lanenumber):
                laneid = edgeid + '_' + str(ln)
                # print(laneid)
                vehiclelist = list(traci.lane.getLastStepVehicleIDs(laneid))
                location = np.array(
                    [traci.vehicle.getDistance(v) - self.get_lastlane_length(v, edgeid) for v in vehiclelist])
                num = [np.count_nonzero(np.where((location > x) & (location < x + self.min_length))) for x in
                       self.lane_divide]
                vehicle_density.append(num)
        return vehicle_density

    def step(self, action):
        actions = self.Onehot2numpy.num_2_bit(action)

        vehicle_density = []
        speed = []
        all_changetimes = []
        total_change = 0
        vehicle_id = traci.vehicle.getIDList()
        for v in vehicle_id:
            lane_id = traci.vehicle.getLaneID(v)
            print('查询',v,lane_id)
            if lane_id in list(self.action_choose.keys()):

                leader = traci.vehicle.getLeader(v)
                v_s = traci.vehicle.getSpeed(v)
                if leader:
                    pre_id, pre_d = leader
                    pre_s = traci.vehicle.getSpeed(pre_id)
                    acc = self.Gipps.carfollowing(v_s, [pre_d, pre_s], v_max=traci.lane.getMaxSpeed(lane_id))
                else:
                    acc = self.Gipps.carfollowing(v_s, None, v_max=traci.lane.getMaxSpeed(lane_id))

                traci.vehicle.setLaneChangeMode(v, 0)
                traci.vehicle.setSpeedMode(v, 32)
                # traci.vehicle.setSpeed(v, 40)
                # traci.vehicle.setAccel(v, acc)
                #
                if v[:6] == "flow_1":
                    print('速度',v,traci.vehicle.getSpeed(v))
                loc = traci.vehicle.getLanePosition(v)
                lane_index = np.array(self.action_choose[lane_id]) #车道检索
                loc_index = self.get_index(loc)  #位置检索
                lane_action = actions[lane_index[0]*20:20*np.sum(lane_index[:2])]
                if lane_index[1] == 2:#如果是位于中间车道
                    lane_action = lane_action[::2] * 2 + lane_action[1::2]

                v_action = lane_action[loc_index]
                # changetimes = traci.vehicle.getParameter(v, 'change times')
                # if changetimes == '':
                #     c = 0
                # else:
                #     c = int(changetimes)
                #
                # targetlane = self.get_targetlane(lane_id,v_action)
                # # print('action',v,v_action,targetlane,lane_id)
                # if targetlane:
                #     print('action',v,v_action,targetlane,lane_id)
                #     total_change += 1
                #     c += 1
                #     traci.vehicle.setParameter(v,'change times',str(c))
                #     traci.vehicle.changeLane(v,targetlane,4)
                #
                # all_changetimes.append(c)

        traci.simulationStep()

        collide = traci.simulation.getCollidingVehiclesIDList()

        for edgeid in self.edgelist:
            onramp = 0
            num_std = []
            lanenumber = traci.edge.getLaneNumber(edgeid)
            v_num_lane = []
            for ln in range(lanenumber):
                laneid = edgeid + '_' + str(ln)
                v_num_lane.append(traci.lane.getLastStepVehicleNumber(laneid))
                vehiclelist = list(traci.lane.getLastStepVehicleIDs(laneid))
                for v in vehiclelist:
                    speed.append(traci.vehicle.getSpeed(v))
                    if laneid == "gneE7_0":
                        onramp += traci.lane.getLength(laneid)-traci.vehicle.getLanePosition(v)
            num_std.append(np.std(np.array(v_num_lane)))
        rewards = self.get_reward(all_changetimes, speed,num_std,total_change,collide,onramp)

        vehicle_density = self.get_state()
        return [vehicle_density, rewards]

    def get_reward(self, all_changetimes, speed,num_std,total_change,collide,onramp):
        lamuda_speed = 0.4
        lamuda_change = 0.15
        lamuda_density = 0.3
        lamuda_total_change = 0.15
        r_speed = np.sum(speed) / len(speed)
        r_change_single = -1 * np.sum(np.trunc(np.array(all_changetimes) / 5))
        r_change_total = -1 * total_change
        # r_change = -1 * (np.count_nonzero(np.where(((np.array(all_changetimes) > 3)))) > 5)
        r_density = - np.sum(num_std)
        r_collide = -1 * pow(10,len(collide))
        r_onramp = - onramp
        # print('reward',r_speed, r_density, r_change_total,r_change_single,r_collide)

        return lamuda_speed * r_speed + lamuda_density * r_density + lamuda_change * r_change_single + lamuda_total_change * r_change_total + r_collide + r_onramp

    def get_index(self,loc):
        x = 0
        loc_index = np.where((self.lane_divide <= loc - x) & (self.lane_divide + self.min_length >= loc  - x))
        # print('loc_index',lane_id,loc_index,loc,self.lane_divide,self.lane_divide + self.min_length,(self.lane_divide <= loc - x),(self.lane_divide + self.min_length >= loc  - x))
        return loc_index[0][0]


    def get_length(self,e):
        lane = e + '_0'
        return traci.lane.getLength(lane)

    def get_lastlane_length(self,v, edgeid):
        route = list(traci.vehicle.getRoute(v))
        loc = route.index(edgeid)
        edgelengthlist = [self.get_length(e) for e in route]
        # print(edgelengthlist)
        edgelengthlist[loc:] = (0,)

        length = sum(edgelengthlist)
        # print(route, edgeid, loc, edgelengthlist, length)
        return length

    def exponential_func(self, x, a):  # 定义指数函数
        y = math.pow(a, x)

        return y

    def get_scenario_vehids(self):
        """获取当前场景的车辆id"""

        return traci.vehicle.getIDList()
    
    def get_targetlane(self,lane_id,act):#0为不变，1向右，2向左
        lanes = self.action_choose[lane_id][-1]
        if act == 0:
            return False
        elif act == 1:
            return lanes[0]
        elif act == 2 and len(lanes) == 2:
            return lanes[1]
        else:
            return False


        # if action == 1 or lane_id == "gneE7_0":
        #     return False
        # else:
        #     if lane_index == 0:#在最右侧
        #         if action == 2:#输出为向左换道
        #             return 1
        #         else:
        #             return False
        #     elif lane_index == 4 or (lane_index == 3 and (lane_id[:5] == "gneE4" or lane_id[:5] == "gneE6")):
        #         if action == 0:
        #             return 3
        #         else:
        #             return False
        #     elif (lane_index == 3 and lane_id[:5] == "gneE5") or lane_index == 2:
        #         return action + lane_index -1
        #
        #     # else:
        #     #     if action == 0:
        #     #         return 2

    def set_lanechangemode(self, vehid):
        """设置换道模式"""
        traci.vehicle.setLaneChangeMode(vehid, 1621)

    def simulationstep(self):
        """仿真一步"""
        time.sleep(0.0001)
        traci.simulationStep()

    def close(self, para):
        traci.close(para)


if __name__ == "__main__":
    E = SumoEnv()
    E.reset()
    for t in range(1000):
        E.step(0)
    # E.close(False)