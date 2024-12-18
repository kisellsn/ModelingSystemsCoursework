from copy import deepcopy

import numpy as np

from client import Client
from fun_rand import FunRand

SPEED_MIN = 30
SPEED_MAX = 40


class Element:
    nextId = 0

    def __init__(self, name=None, delay_mean=1., delay_dev=0., distribution='', n_channel=1,
                 max_queue=float('inf')):
        self.t_next = [0] * n_channel  # момент часу наступної події
        self.delay_mean = delay_mean  # середнє значення часової затримки
        self.delay_dev = delay_dev  # середнє квадратичне відхилення часової затримки
        self.quantity = 0
        self.t_curr = 0  # поточний момент часу
        self.state = [0] * n_channel
        self.next_element = None  # вказує на наступний (в маршруті слідування вимоги) елемент моделі
        self.id_el = Element.nextId
        Element.nextId += 1
        self.name = f'Element_{self.id_el}' if name is None else name
        self.distribution = distribution

        self.priority = [1]
        self.queue = 0
        self.max_observed_queue = 0
        self.max_queue = max_queue
        self.mean_queue = 0.0
        self.channel = n_channel
        self.mean_load = 0
        self.failure = 0

        self.next_client = Client()

        self.transition_period = 0

    def choose_next_element(self):
        if self.priority != [1]:
            next_element = self.choose_by_priority()
            return next_element
        elif self.priority == [1]:
            return self.next_element[0]

    def choose_by_priority(self):
        priorities = deepcopy(self.priority)

        for p in range(len(priorities)):
            max_pr_index = priorities.index(min(priorities))  # pr = 1
            min_pr_index = priorities.index(max(priorities))  # pr = 2

            if self.name == 'Operators':
                if (self.next_element[min_pr_index].queue < 10 or
                        self.next_client.get_attempt_num() >= self.next_client.max_attempts):
                    return self.next_element[min_pr_index]
                elif self.next_client.get_attempt_num() < self.next_client.max_attempts:
                    return self.next_element[max_pr_index]

            elif self.name == 'Dialing':
                if (not self.next_element[min_pr_index].get_free_channels() and
                        self.next_client.get_attempt_num() < self.next_client.max_attempts):
                    return self.next_element[max_pr_index]
                else:
                    return self.next_element[min_pr_index]

    def get_delay(self):
        if self.name == 'Taxis':
            distance_to = np.random.choice([5, 8, 9, 11, 12, 20], p=[0.1, 0.2, 0.25, 0.17, 0.23, 0.05])
            self.next_client.set_distance_to(distance_to)

            speed = FunRand.uniform(SPEED_MIN, SPEED_MAX) / 60  # у км/хв
            service_time = FunRand.uniform(self.delay_mean - self.delay_dev,
                                           self.delay_mean + self.delay_dev)

            distance_from = speed * service_time  # distance from client to endtpoint
            self.next_client.set_distance_from(distance_from)

            return self.next_client.get_distance_to() / speed + service_time  # time to client + service
        elif self.name == 'Dialing':
            call_delay = self.next_client.dialing_time
            if self.next_client.get_attempt_num() > 1:
                call_delay += self.next_client.waiting_time
            return call_delay
        else:
            if 'exp' == self.distribution:
                return FunRand.exp(self.delay_mean)
            elif 'erlang' == self.distribution:
                return FunRand.erlang(self.delay_mean, self.delay_dev)
            elif 'uniform' == self.distribution:
                return FunRand.uniform(self.delay_mean - self.delay_dev, self.delay_mean + self.delay_dev)
            else:
                return self.delay_mean

    def in_act(self, next_client):  # вхід в елемент
        pass

    def get_state(self):
        return self.state

    def set_state(self, new_state):
        self.state = new_state

    def set_t_next(self, t_next_new):
        self.t_next = t_next_new

    def get_t_curr(self):
        return self.t_curr

    def get_name(self):
        return self.name

    def out_act(self):  # вихід з елементу
        if self.t_curr >= self.transition_period:
            self.quantity += 1

    def result(self):
        print(f'{self.name} quantity = {str(self.quantity)} state = {self.state}')

    def print_info(self):
        print(f'{self.name} state = {self.state} quantity = {self.quantity} t_next = {self.t_next}')

    def calculate(self, delta):
        self.mean_queue += self.queue * delta

        if self.queue > self.max_observed_queue:
            self.max_observed_queue = self.queue

        for i in range(self.channel):
            self.mean_load += self.state[i] * delta

        self.mean_load = self.mean_load / self.channel

    def calculate_mean(self, delta):
        pass

    def get_free_channels(self):
        free_channels = []
        for i in range(self.channel):
            if self.state[i] == 0:
                free_channels.append(i)

        return free_channels

    def get_current_channel(self):
        current_channels = []
        for i in range(self.channel):
            if self.t_next[i] == self.t_curr:
                current_channels.append(i)
        return current_channels

    def set_transition_period(self, t):
        self.transition_period = t
