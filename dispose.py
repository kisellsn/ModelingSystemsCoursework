import numpy as np

from element import Element


class Dispose(Element):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.t_next = [np.inf]
        self.delta_t_service = 0
        self.total_distance_from = 0
        # self.count_cals = 0
        # self.max_c = 0

    def in_act(self, next_client):
        if next_client.get_t_start() is not None:
            self.delta_t_service += self.t_curr - next_client.get_t_start()
            self.total_distance_from += next_client.get_distance_from()

            # self.count_cals += next_client.get_attempt_num()
            # if next_client.get_attempt_num() >= self.max_c:
            #     self.max_c = next_client.get_attempt_num()
        super().out_act()
