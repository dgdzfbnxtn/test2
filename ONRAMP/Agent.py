import numpy as np
import pandas as pd
# import os
# import random
# from collections import deque
from tensorflow.keras import models, layers, optimizers

# os.environ["CUDA_VISIBLE_DEVICES"] = "0"


# 经验回放
class Replayer(object):
    def __init__(self, capacity):
        self.memory = pd.DataFrame(index=range(capacity),
                                   columns=['observation', 'action', 'reward',
                                            'next_observation'])
        self.i = 0
        self.count = 0
        self.capacity = capacity

    def store(self, *args):
        self.memory.loc[self.i] = args
        self.i = (self.i + 1) % self.capacity
        self.count = min(self.count + 1, self.capacity)

    def sample(self, size):
        indices = np.random.choice(self.count, size=size)
        return (np.stack(self.memory.loc[indices, field]) for field in \
                self.memory.columns)


class Agent(object):
    def __init__(self, state_size, action_size, gamma=0.99, epsilon=0.1, min_epsilon=0.001, epsilon_decrease_rate=0.003):
        self.state_size = state_size
        self.action_size = action_size
        self.step = 0
        self.update_freq = 200  # 模型更新频率
        self.replay_size = 1000  # 训练集大小
        # self.replay_queue = deque(maxlen=self.replay_size)
        self.replayer = Replayer(capacity=self.replay_size)

        self.evaluate_net = self.create_model()
        self.target_net = self.create_model()

        self.epsilon = epsilon
        self.min_epsilon = min_epsilon
        self.epsilon_decrease_rate = epsilon_decrease_rate
        self.gamma = gamma

    def create_model(self):
        """创建一个隐藏层为100的神经网络"""
        STATE_DIM, ACTION_DIM = self.state_size, self.action_size  # 需要修改
        model = models.Sequential([
            layers.Dense(100, input_dim=STATE_DIM, activation='relu'),
            layers.Dense(100, activation='relu'),
            layers.Dense(ACTION_DIM, activation="linear")
        ])
        model.compile(loss='mean_squared_error',
                      optimizer=optimizers.Adam(0.001))
        return model

    def decide(self, observation, random=False):   # 需要修改
        if random or np.random.rand() < self.epsilon:
            return np.random.choice(range(self.action_size))
        qs = self.evaluate_net.predict(observation.reshape(1, self.state_size))

        return np.argmax(qs)

    def save_model(self, file_path):
        print('model saved')
        self.evaluate_net.save(file_path)

    def remember(self, s, a, reward, next_s):
        """历史记录"""
        self.replayer.store(s, a, reward, next_s)

    def train(self, batch_size=64):
        # self.replayer.store(observation, action, reward, next_observation)  # 存储经验

        if self.replayer.count < self.replay_size:
            return
        self.step += 1
        # 每 update_freq 步，将 model 的权重赋值给 target_model
        if self.step % self.update_freq == 0:
            self.target_net.set_weights(self.evaluate_net.get_weights())

        observations, actions, rewards, next_observations = \
            self.replayer.sample(batch_size)  # 经验回放

        next_qs = self.target_net.predict(next_observations)
        next_max_qs = next_qs.max(axis=-1)
        us = rewards + self.gamma * next_max_qs
        targets = self.evaluate_net.predict(observations)
        targets[np.arange(us.shape[0]), actions] = us
        history = self.evaluate_net.fit(observations, targets, verbose=0)
        # print(history.history)
        # print(self.evaluate_net.summary())

        # 减小 epsilon 的值
        self.epsilon -= self.epsilon_decrease_rate
        self.epsilon = max(self.epsilon, self.min_epsilon)
        print('训练Agent一次')

