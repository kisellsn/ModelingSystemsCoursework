
class Client:
    def __init__(self):
        self.max_attempts = 4
        self.dialing_time = 0.5
        self.waiting_time = 1

        self.attempt_num = 0
        self.distance_to = None  # distance from taxi to client
        self.distance_from = None  # distance from client to endpoint
        self.t_start = None

    def set_distance_from(self, distance_from):
        self.distance_from = distance_from

    def set_distance_to(self, distance_to):
        self.distance_to = distance_to

    def set_t_start(self, t_start):
        self.t_start = t_start

    def make_call(self):
        self.attempt_num += 1

    def get_distance_to(self):
        return self.distance_to

    def get_distance_from(self):
        return self.distance_from

    def get_t_start(self):
        return self.t_start

    def get_attempt_num(self):
        return self.attempt_num
