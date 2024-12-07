import numpy as np

from dispose import Dispose
from process import Process


class Model:
    def __init__(self, elements: list, transition_period=0):
        self.list = elements
        self.event = 0
        self.t_next = 0.0
        self.t_curr = self.t_next

        self.response_times = []  # Список для збереження середнього часу виконання замовлень
        self.time_interval = 100  # Інтервал часу для фіксації даних
        self.next_record_time = self.time_interval
        self.transition_period = transition_period

        self.standard_deviations = []

    # здійснення імітації на інтервалі часу time
    def simulate(self, time):
        while self.t_curr < time:
            self.t_next = float('inf')

            for e in self.list:
                t_next_val = np.min(e.t_next)
                if t_next_val < self.t_next:
                    self.t_next = t_next_val
                    self.event = e.id_el
            # try:
            #     print(f'\nIt\'s time for event in {self.list[self.event].get_name()}, time ={self.t_next}\n')
            # except IndexError:
            #     pass

            for e in self.list:
                e.calculate(self.t_next - self.t_curr)

            self.t_curr = self.t_next

            for e in self.list:
                e.t_curr = self.t_curr

            if len(self.list) > self.event:
                self.list[self.event].out_act()

            for e in self.list:
                if self.t_curr in e.t_next:
                    e.out_act()

            # Збирання статистики кожні 100 одиниць часу
            if self.t_curr >= self.next_record_time:
                # Тільки після перехідного періоду
                if not self.transition_period and self.t_curr > self.transition_period:
                    self.record_response_time()
                self.next_record_time += self.time_interval

            # self.print_info()
        # self.print_result()
        return self.response_times

    def record_response_time(self):
        # Розрахунок середнього часу виконання замовлень
        total_response_time = 0
        total_clients = 0
        for e in self.list:
            if isinstance(e, Dispose):
                total_response_time += e.delta_t_service
                total_clients += e.quantity

        average_response_time = total_response_time / total_clients if total_clients > 0 else 0
        self.response_times.append(average_response_time)
        # print(f"Recorded average response time at time {self.t_curr}: {average_response_time}")

    def print_info(self):
        for e in self.list:
            e.print_info()

    def print_result(self):
        print('-----RESULT-----')
        cost_per_km = 3
        salary = 1000

        global_max_observed_queue_length = 0
        global_mean_queue_length_accumulator = 0
        global_failure_probability_accumulator = 0
        global_mean_load_accumulator = 0
        global_mean_time_service_accumulator = 0
        num_of_finished = 0

        fixed_revenue = 0
        total_distance = 0
        num_of_processors = 0
        num_of_workers = -1  # -1 bc of dialing_processor

        for e in self.list:
            e.result()
            if isinstance(e, Process):
                num_of_processors += 1
                num_of_workers += e.channel

                # Середня довжина черги
                mean_queue_length = e.mean_queue / self.t_curr
                global_mean_queue_length_accumulator += mean_queue_length

                # Ймовірність відмови
                failure_probability = e.failure / (e.quantity + e.failure) if (e.quantity + e.failure) != 0 else 0
                global_failure_probability_accumulator += failure_probability

                # Середнє завантаження
                mean_load = e.mean_load / self.t_curr
                global_mean_load_accumulator += mean_load

                # Максимальна спостережувана довжина черги
                if e.max_observed_queue > global_max_observed_queue_length:
                    global_max_observed_queue_length = e.max_observed_queue

                print(f"Processor: {e.name}")
                print(f"  Average queue length: {mean_queue_length:.2f}")
                print(f"  Failure probability: {failure_probability:.2%}")
                print(f"  Average load: {mean_load:.4f}")
                print()

                # Додаткові метрики для таксі
                if e.name == 'Taxis':
                    fixed_revenue += e.quantity * 20  # Фіксована плата за замовлення
            elif isinstance(e, Dispose):
                if e.name == 'EXIT1':
                    global_mean_time_service_accumulator += e.delta_t_service
                    total_distance = e.total_distance_from
                    num_of_finished += e.quantity
                    # print(e.count_cals / num_of_finished, e.max_c, num_of_finished)

        # Глобальні метрики
        global_mean_queue_length = global_mean_queue_length_accumulator / num_of_processors
        global_failure_probability = global_failure_probability_accumulator / num_of_processors
        global_mean_load = global_mean_load_accumulator / num_of_processors
        global_mean_time_service = global_mean_time_service_accumulator / num_of_finished

        print(f"Global max observed queue length: {global_max_observed_queue_length}")
        print(f"Global mean queue length: {global_mean_queue_length:.2f}")
        print(f"Global failure probability: {global_failure_probability:.2%}")
        print(f"Global mean time of taxi service: {global_mean_time_service:.2f}")
        print(f"Global mean load: {global_mean_load:.4f}")

        # Прибуток
        total_revenue = fixed_revenue + total_distance * cost_per_km
        net_profit = total_revenue - (salary * num_of_workers * self.t_curr / 1440)
        print(f"Total revenue: {total_revenue:.4f} UAH")
        print(f"Total expenses: {(salary * num_of_workers * self.t_curr / 1440)} UAH")
        print(f"Total distance: {total_distance:.2f}")
        print(f"Net profit: {net_profit} UAH")
        print()
