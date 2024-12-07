import numpy as np
import element as e
from fun_rand import FunRand
from client import Client


class Process(e.Element):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.t_next = [np.inf] * self.channel
        self.state = [0] * self.channel

        self.clients = [Client(None)] * self.channel  # клієнти для кожного робітника
        self.clients_queue = []  # масив клієнтів в черзі

    def in_act(self, client):
        self.next_client = client

        if self.name == 'Taxis':
            self.next_client.set_t_start(self.t_curr)

        if self.name == 'Operators' and self.next_client.get_attempt_num() > self.next_client.max_attempts:
            if self.t_curr > self.transition_period:
                self.failure += 1
            return

        if self.name == "Dialing":
            self.next_client.make_call()

        free_worker = self.get_free_channels()
        if len(free_worker) > 0:
            i = free_worker[0]
            self.state[i] = 1
            self.t_next[i] = self.t_curr + super().get_delay()

            self.clients[i] = self.next_client
        else:
            if self.queue < self.max_queue:
                self.queue += 1
                self.clients_queue.append(self.next_client)
            else:
                # Якщо є можливість повторного виклику
                if self.name == 'Operators' and self.next_client.get_attempt_num() < self.next_client.max_attempts:
                    retry_processor = self.next_element[1]
                    retry_processor.in_act(self.next_client)
                else:
                    if self.t_curr > self.transition_period:
                        self.failure += 1

    def out_act(self):
        current_channel = self.get_current_channel()
        for i in current_channel:
            super().out_act()
            self.t_next[i] = np.inf
            self.state[i] = 0

            prev_client = self.clients[i]
            self.clients[i] = Client(None)

            if self.queue > 0:
                self.queue -= 1
                self.next_client = self.clients_queue.pop(0)

                self.state[i] = 1
                self.t_next[i] = self.t_curr + super().get_delay()

                self.clients[i] = self.next_client

            if self.next_element is not None:
                self.next_client = prev_client
                next_element = self.choose_next_element()
                if next_element is not None:
                    next_element.in_act(self.next_client)
