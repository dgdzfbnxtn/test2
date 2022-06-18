# import sys
# print(sys.path)

import numpy as np
import matplotlib.pyplot as plt

from Env import SumoEnv

from Agent import Agent


class Environment(object):
    def __init__(self):
        self.env = SumoEnv()
        self.MAXTIME = 600
        self.EPISODE = 1000

    def run(self, agent):

        total_step = 0
        timesteps_list = []
        episodes_rewards_list = []  # 所有回合中，各回合每个智能体的总奖励
        states = self.env.reset()
        for episode_num in range(self.EPISODE):

            # reward_all = 0
            rewards_all = 0
            time_step = 0
            t = 0
            while t < self.MAXTIME:
                t += 1
                states = self.env.get_state()
                actions = agent.decide(np.array(states))
                next_states, rewards = self.env.step(actions)
                agent.remember(np.array(states), actions, rewards, np.array(next_states))
                rewards_all += rewards

                try:
                    agent.train()
                except Exception as e:
                    pass

                total_step += 1
                states = next_states

            episodes_rewards_list.append(rewards_all)

            timesteps_list.append(time_step)
            # self.env.close(False)
            print("Episode {p}, Final Step: {t}".format(p=episode_num, t=time_step))
            print('回合奖励', rewards_all)
            file_path = 'model_saved\\' + 'agent'+str(episode_num) +str(t)+ '.h5'
            agent.save_model(file_path)

            # self.env.close(False)

        file_path = 'model_saved' + 'agent' + '.h5'
        agent.save_model(file_path)


if __name__ == "__main__":

    env = Environment()
    state_size = env.env.state_size
    action_size = 3

    agent = Agent(state_size, action_size)

    env.run(agent)