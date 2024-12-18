import numpy as np

from element import Element


class Dispose(Element):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.t_next = [np.inf]
        self.delta_t_service = 0
        self.total_distance_from = 0

    def in_act(self, next_client):
        if next_client.get_t_start() is not None:
            if self.t_curr > self.transition_period:
                self.delta_t_service += self.t_curr - next_client.get_t_start()
                self.total_distance_from += next_client.get_distance_from()

        super().out_act()
