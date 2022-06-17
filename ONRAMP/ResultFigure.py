#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @TIme      : 2022/1/24 1:20
# @Author    : Bingmei Jia
# @Site      : 
# @File      : ResultFigure.py
# @Software  : PyCharm

import pandas as pd
import matplotlib.pyplot as plt

def log_read(file=r'logs\2022-01-24_02_baseline_seed=0.log'):
    lst_log = []
    log_dir = file
    with open(log_dir, encoding='utf-8') as log_etl:
        for line in log_etl:
            # 逐行读取数据 ，只取有效数据
            if '|' in line:
                lst_log.append(line.strip())
    df_etllog = pd.DataFrame({'message': lst_log})
    df_etllog.head()
    # print(df_etllog)
    df_etllog = data_parser(df_etllog)
    return df_etllog

def data_parser(df_etllog):
    df_etllog1 = df_etllog['message'].str.split('|', expand=True)
    # 重命名列
    df_etllog1.columns = ['ep', 'step', 'reward', 'length', 'hours']
    df_etllog2 = df_etllog1.join(df_etllog)
    return df_etllog2
    # print(df_etllog2['step'])

def reward_figure(df):
    reward = df['reward'].str.split('=', expand=True)
    reward.columns = ['name1', 'reward']
    episode = df['ep'].str.split('=', expand=True)
    episode.columns = ['name2', 'episode']

    ep = reward.join(episode)

    fig,ax = plt.subplots()
    plt.plot(ep['episode'][::3],ep['reward'][::3])

    plt.show()



df_etllog=log_read()
reward_figure(df_etllog)