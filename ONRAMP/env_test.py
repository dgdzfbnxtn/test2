#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @TIme      : 2022/1/23 20:27
# @Author    : Bingmei Jia
# @Site      : 
# @File      : env_test.py
# @Software  : PyCharm

import gym
env = gym.make('BreakoutNoFrameskip-v0')
env.reset()
for _ in range(1000):
    env.render()
    observation, reward, done, info = env.step(env.action_space.sample())
    if done:
        env.reset()
env.close()
