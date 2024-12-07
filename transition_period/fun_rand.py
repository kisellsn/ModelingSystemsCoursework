import random
import numpy as np

class FunRand:
    @staticmethod
    def exp(time_mean):
        a = 0.0
        while a == 0:
            a = random.random()
        a = -time_mean * np.log(a)
        return a

    @staticmethod
    def erlang(time_mean, k=2):
        total_time = 0
        for _ in range(k):
            total_time += FunRand.exp(time_mean / k)
        return total_time

    @staticmethod
    def uniform(time_min, time_max):
        a = random.random()
        a = time_min + a * (time_max - time_min)
        return a
