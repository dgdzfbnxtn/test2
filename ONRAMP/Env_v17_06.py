"""
DQN
全部为智能网联车
状态：每辆车的目标转向车道、每辆车所在车道的索引、每辆车旁边两条车道后面一段范围内车的换道需求、信号灯状态
奖励：
每辆车和目标转向车道的距离。
车辆换道后，对目标车道后车的影响。影响范围多长？
对于换道次数的惩罚。
每个回合，所有车辆加入到对应目标转向车道就结束训练。

考虑信号灯和两侧车辆
改进奖励函数、状态、超参数
"""
import traci
import math
import os
import sys
import time
import random
from sumolib import checkBinary


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
        self.left_couldchangelane = None
        self.right_couldchangelane = None

        self.lanes_num = lanes_num

    def get_desired_lane(self):
        """得到期望车道"""
        routeid = traci.vehicle.getRouteID(self.veh_id)
        if routeid == 'route0':
            self.desired_lane = 0
        elif routeid == 'route1':
            self.desired_lane = random.randint(3, 4)
        else:
            self.desired_lane = random.randint(1, 2)

        return self.desired_lane

    def get_lane_index(self):
        """得到所在车道索引"""
        self.lane_index = traci.vehicle.getLaneIndex(self.veh_id)

        return self.lane_index

    def get_speed(self):
        """得到车辆速度"""
        self.speed = traci.vehicle.getSpeed(self.veh_id)

        return self.speed

    def get_lanespeed(self, lanes_ids):
        self.lanespeed = traci.lane.getLastStepMeanSpeed(lanes_ids[self.lane_index])

        return self.lanespeed

    def get_couldchangelane(self):
        """判断是否能换道"""
        if self.lane_index == 0:
            self.right_couldchangelane = 0
            self.left_couldchangelane = int(traci.vehicle.couldChangeLane(self.veh_id, 1))
        elif self.lane_index == (self.lanes_num - 1):
            self.right_couldchangelane = int(traci.vehicle.couldChangeLane(self.veh_id, -1))
            self.left_couldchangelane = 0
        else:
            self.right_couldchangelane = int(traci.vehicle.couldChangeLane(self.veh_id, -1))
            self.left_couldchangelane = int(traci.vehicle.couldChangeLane(self.veh_id, 1))

        return self.right_couldchangelane, self.left_couldchangelane

    def get_dist_to_light(self, lane_len):
        self.dist_to_light = lane_len - traci.vehicle.getLanePosition(self.veh_id)

        return self.dist_to_light

    def get_light_state(self):
        """得到信号灯状态：当前相位、转到下一相位的剩余时间"""
        phase = traci.trafficlight.getPhase("gneJ1")
        print('相位索引', phase)
        self.int_phase = phase
        self.remain_duration = traci.trafficlight.getNextSwitch("gneJ1") - traci.simulation.getTime()  # 转换到下一个相位的剩余时间

        return self.int_phase, self.remain_duration

    def change_lane(self):
        """根据目标车道执行换道"""
        traci.vehicle.changeLane(self.veh_id, self.target_lane, 1)  # 可修改

    def get_targetlane(self, act):
        """根据动作计算目标车道"""
        if act == 0:
            if self.lane_index == 0:
                act = 2
        elif act == 1:
            if self.lane_index == self.lanes_num - 1:
                act = 2
        else:
            act = act

        if act == 0:
            self.target_lane = self.lane_index - 1
        elif act == 1:
            self.target_lane = self.lane_index + 1
        else:
            self.target_lane = self.lane_index

        return self.target_lane

    def set_speed(self, vmax):
        """执行加速"""
        speed = min(self.speed + 1, vmax)
        traci.vehicle.setSpeed(self.veh_id, speed)


class SumoEnv(object):  # 考虑单车的奖励不一样
    RIGHT = 0
    LEFT = 1
    STAY = 2
    A = [RIGHT, LEFT, STAY]

    def __init__(self, laneids, vehids):
        self.lanes_ids = laneids  # 车道id
        self.vehicles_ids = vehids  # 被控制车辆id
        self.lanes_num = len(self.lanes_ids)
        self.vehicles_num = len(self.vehicles_ids)
        self.vmax = 16
        self.lane_len = 1000
        self.state_size = 8  # 分为全局和局部状态

        self.vehicles = []
        for veh_id in vehids:  # 存储顺序
            self.vehicles.append(Vehicle(veh_id, self.lanes_num))

        self.desired_lanes = {}
        self.terminal = False

        if 'SUMO_HOME' in os.environ:
            tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
            sys.path.append(tools)
        else:
            sys.exit("please declare environment variable 'SUMO_HOME'")

        if_show_gui = False
        if not if_show_gui:
            self.sumoBinary = checkBinary("sumo")
        else:
            self.sumoBinary = checkBinary("sumo-gui")
        self.sumocfgfile = "C:\\sumo-1.3.1\\file\\simulation1_v1\\exa.sumocfg"

    def reset(self):
        traci.start([self.sumoBinary, "-c", self.sumocfgfile])
        phase = random.randint(0, 3)
        if phase == 0:
            phaseduration = random.randint(0, 39)
        elif phase == (1 or 3):
            phaseduration = random.randint(0, 2)
        else:
            phaseduration = random.randint(0, 29)
        traci.trafficlight.setPhase("gneJ1", phase)
        traci.trafficlight.setPhaseDuration("gneJ1", phaseduration)

        while True:  # 确保被控车辆全部进入场景
            # time.sleep(1)
            traci.simulationStep()
            all_vehids = []
            for key in self.lanes_ids:
                sub_vehids = traci.lane.getLastStepVehicleIDs(self.lanes_ids[key])
                all_vehids.extend(sub_vehids)
            print('当前场景车辆的ID', all_vehids)
            if set(self.vehicles_ids).issubset(set(all_vehids)):
                break

        for vehid in self.vehicles_ids:
            traci.vehicle.setLaneChangeMode(vehid, 512)
            # traci.vehicle.setSpeedMode(vehid, 31)

        self.desired_lanes = {}
        for veh in self.vehicles:
            self.desired_lanes[veh.veh_id] = veh.get_desired_lane()

        initial_states = []
        for veh in self.vehicles:
            veh_state = [veh.desired_lane, veh.get_lane_index(), veh.get_speed(), veh.get_dist_to_light(self.lane_len),
                         veh.get_couldchangelane()[0], veh.get_couldchangelane()[1],
                         veh.get_light_state()[0], veh.get_light_state()[1]]
            initial_states.append(veh_state)
        print('初始状态', initial_states)

        return initial_states

    def step(self, actions):
        print('期望车道', self.desired_lanes)
        # print('step前车道', [veh.get_lane_index() for veh in self.vehicles])
        for index, veh in enumerate(self.vehicles):
            if actions[index] == 10:  # 在其它道路上或不在场景中
                pass
            # elif actions[index] == 100:  # 不在场景中
            #     pass
            # elif actions[index] == 3:  # 加速
            #     veh.set_speed(self.vmax)
            else:  # 换道
                veh.get_targetlane(actions[index])
                veh.change_lane()
        traci.simulationStep()

        rewards = [0 for i in range(len(self.vehicles))]
        arrives = []
        new_states = []
        for index, veh in enumerate(self.vehicles):
            arrive = False
            if veh.veh_id not in self.get_scenario_vehids():  # 不在场景中
                reward = 0
                desired_lane = -1
                lane_index = -1
                speed = -1
                dist_to_light = -1
                couldchangelane = (-1, -1)
                light_state = (-1, -1)
                arrive = True
            else:  #
                x_veh = traci.vehicle.getLanePosition(veh.veh_id)
                roadid = traci.vehicle.getRoadID(veh.veh_id)
                if roadid != 'gneE0':  # 在其他道路上
                    reward = 0
                    desired_lane = -1
                    lane_index = -1
                    speed = -1
                    dist_to_light = -1
                    couldchangelane = (-1, -1)
                    light_state = (-1, -1)
                    arrive = True
                else:
                    gap = abs(veh.desired_lane - veh.get_lane_index())
                    reward1 = 0
                    if (x_veh - self.lane_len) >= -20:  # 到达时为绿灯奖励
                        if veh.desired_lane == (0 or 1 or 2):
                            if veh.get_light_state()[0] == 0:
                                reward1 = 10
                            else:
                                reward1 = 0
                        elif veh.desired_lane == (3 or 4):
                            if veh.get_light_state()[0] == 2:
                                reward1 = 10
                            else:
                                reward1 = 0
                        else:
                            reward1 = 0
                    if gap == 0:
                        reward2 = 0  # 根据期望车道和所在车道距离给出惩罚
                    else:
                        coefficient1 = self.exponential_func(x_veh/100, 2.1) / 400
                        reward2 = -coefficient1 * gap * 2
                    if actions[index] == (0 or 1):  # 换道惩罚
                        coefficient2 = self.exponential_func(x_veh / 100, 1.2) / 2.5
                        reward3 = -2 * coefficient2
                    else:
                        reward3 = 0
                    if (actions[index] == (0 or 1)) and (veh.lane_index != veh.target_lane):  # 换道不成功惩罚
                        coefficient3 = self.exponential_func(x_veh / 100, 1.4) / 10
                        reward4 = -2 * coefficient3
                    else:
                        reward4 = 0
                    reward = reward1 + reward2 + reward3 + reward4

                    desired_lane = veh.desired_lane
                    lane_index = veh.get_lane_index()
                    speed = veh.get_speed()
                    dist_to_light = veh.get_dist_to_light(self.lane_len)
                    couldchangelane = veh.get_couldchangelane()
                    light_state = veh.get_light_state()

                    if (x_veh - self.lane_len) >= -20:
                        arrive = True

            rewards[index] = reward
            arrives.append(arrive)
            veh_state = [desired_lane, lane_index, speed, dist_to_light, couldchangelane[0], couldchangelane[1],
                         light_state[0], light_state[1]]
            new_states.append(veh_state)

        print('step后状态', new_states)
        # print('step后车道', [veh.get_lane_index() for veh in self.vehicles])

        return [new_states, rewards, arrives]

    def exponential_func(self, x, a):  # 定义指数函数
        y = math.pow(a, x)

        return y

    def get_scenario_vehids(self):
        """获取当前场景的车辆id"""

        return traci.vehicle.getIDList()

    def set_lanechangemode(self, vehid):
        """设置换道模式"""
        traci.vehicle.setLaneChangeMode(vehid, 1621)

    def simulationstep(self):
        """仿真一步"""
        time.sleep(1)
        traci.simulationStep()

    def close(self, para):
        traci.close(para)






