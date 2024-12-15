import numpy as np

import element as e
from client import Client


class Create(e.Element):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arrived_before_transition_time = 0

    def out_act(self):
        super().out_act()
        self.t_next[0] = self.t_curr + super().get_delay()

        # next_distance = np.random.choice([5, 8, 9, 11, 12, 20], p=[0.1, 0.2, 0.25, 0.17, 0.23, 0.05])
        # self.next_client = Client(next_distance)
        self.next_client = Client()

        next_element = self.choose_next_element()
        if self.t_curr < self.transition_period:
            self.arrived_before_transition_time += 1
        next_element.in_act(self.next_client)
