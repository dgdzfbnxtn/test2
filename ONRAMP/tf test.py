#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @TIme      : 2022/6/9 15:18
# @Author    : Bingmei Jia
# @Site      : 
# @File      : tf test.py
# @Software  : PyCharm

# from tensorflow.keras import models, layers, optimizers
# import numpy as np
# a = np.array([1,0,0,1,1,1])
# a = 2*a[::2]+a[1::2]
# print(a)
action_choose = {"gneE4_0":[0,1,[1]],"gneE4_1":[7,2,[0,2]],"gneE4_2":[1,1,[1]], "gneE5_0":[4,1,[1]],"gneE5_1":[5,1,[2]],"gneE5_2":[11,2,[1,3]],"gneE5_3":[6,1,[2]],
            "gneE6_0":[2,1,[1]],"gneE6_1":[9,2,[0,2]],"gneE6_2":[3,1,[1]]} #
for i in action_choose:
    print(i)