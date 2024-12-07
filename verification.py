from create import Create
from dispose import Dispose
from process import Process
from model import Model
import pandas as pd



if __name__ == '__main__':
    TOTAL_WORKERS = 15
    NUM_RUNS = 3
    tmod = 1440  # 1 день роботи (1440 хвилин)

    # Параметри для верифікації
    test_cases = [
        {"operators": 5, "call_interval": 3, "dial_time": 0.5, "retry_wait": 1, "order_time": 3,
         "retry_attempts": 4, "max_queue": 10, "base_fare": 20, "km_fare": 3, "worker_salary": 1000},
        # {"operators": 10, "call_interval": 3, "dial_time": 0.5, "retry_wait": 1, "order_time": 3,
        #  "retry_attempts": 4, "max_queue": 10, "base_fare": 20, "km_fare": 3, "worker_salary": 1000},
        # {"operators": 2, "call_interval": 3, "dial_time": 0.5, "retry_wait": 1, "order_time": 3,
        #  "retry_attempts": 4, "max_queue": 10, "base_fare": 20, "km_fare": 3, "worker_salary": 1000},
        # {"operators": 5, "call_interval": 1.5, "dial_time": 0.5, "retry_wait": 1, "order_time": 3,
        #  "retry_attempts": 4, "max_queue": 10, "base_fare": 20, "km_fare": 3, "worker_salary": 1000},
        # {"operators": 5, "call_interval": 3, "dial_time": 1.0, "retry_wait": 1, "order_time": 3,
        #  "retry_attempts": 4, "max_queue": 10, "base_fare": 20, "km_fare": 3, "worker_salary": 1000},
        # {"operators": 5, "call_interval": 3, "dial_time": 0.5, "retry_wait": 2.0, "order_time": 1.5,
        #  "retry_attempts": 4, "max_queue": 10, "base_fare": 20, "km_fare": 3, "worker_salary": 1000},
        # {"operators": 5, "call_interval": 3, "dial_time": 0.5, "retry_wait": 1, "order_time": 3,
        #  "retry_attempts": 2, "max_queue": 10, "base_fare": 20, "km_fare": 3, "worker_salary": 1000},
        # {"operators": 5, "call_interval": 3, "dial_time": 0.5, "retry_wait": 1, "order_time": 1.5,
        #  "retry_attempts": 4, "max_queue": 10, "base_fare": 20, "km_fare": 3, "worker_salary": 1000},
        # {"operators": 5, "call_interval": 3, "dial_time": 0.5, "retry_wait": 1, "order_time": 3,
        #  "retry_attempts": 4, "max_queue": 20, "base_fare": 20, "km_fare": 3, "worker_salary": 1000},
        # {"operators": 5, "call_interval": 3, "dial_time": 0.5, "retry_wait": 1, "order_time": 3,
        #  "retry_attempts": 4, "max_queue": 10, "base_fare": 30, "km_fare": 3, "worker_salary": 1000},
        # {"operators": 5, "call_interval": 3, "dial_time": 0.5, "retry_wait": 1, "order_time": 3,
        #  "retry_attempts": 4, "max_queue": 10, "base_fare": 20, "km_fare": 5, "worker_salary": 1000},
        # {"operators": 5, "call_interval": 3, "dial_time": 0.5, "retry_wait": 1, "order_time": 3,
        #  "retry_attempts": 4, "max_queue": 10, "base_fare": 20, "km_fare": 3, "worker_salary": 1000},
        # {"operators": 5, "call_interval": 3, "dial_time": 0.5, "retry_wait": 1, "order_time": 3,
        #  "retry_attempts": 4, "max_queue": 10, "base_fare": 20, "km_fare": 3, "worker_salary": 900},
    ]

    results = []

    for case in test_cases:
        DIAL = case["dial_time"]
        RETRY = case["retry_wait"]
        AT = case["retry_attempts"]

        operators = case["operators"]
        drivers = TOTAL_WORKERS - operators  # Решта працівників - оператори

        print(f"\nSimulating with {operators} operators and {drivers} drivers...")
        total_net_profit = 0
        total_avg_time_service = 0
        total_serviced_clients = 0
        total_unserviced_clients = 0
        total_revenue = 0

        for run in range(NUM_RUNS):
            # Ініціалізація елементів моделі
            creator = Create(name='Call Generator', delay_mean=case["call_interval"], delay_dev=2,
                             distribution='erlang')
            call_process = Process(name='Operators', delay_mean=case["order_time"], distribution='exp',
                                   n_channel=operators, max_queue=0)
            dialing_processor = Process(name='Dialing', delay_mean=case["retry_wait"], distribution='exp',
                                        max_queue=float('inf'))
            taxi_dispatch = Process(name='Taxis', delay_mean=40, delay_dev=10, distribution='uniform',
                                    n_channel=drivers, max_queue=case["max_queue"])
            d1 = Dispose(name='EXIT1')

            # Ланцюг зв'язків
            creator.next_element = [dialing_processor]
            dialing_processor.next_element = [call_process]
            call_process.next_element = [taxi_dispatch, dialing_processor]
            call_process.priority = [2, 1]
            taxi_dispatch.next_element = [d1]

            # Запуск моделі
            elements = [creator, dialing_processor, call_process, taxi_dispatch, d1]
            model = Model(elements)
            model.simulate(tmod)

            # Результати прогону
            run_serviced_clients = d1.quantity
            run_unserviced_clients = creator.quantity - d1.quantity
            run_revenue = case["base_fare"] * d1.quantity + case["km_fare"] * d1.total_distance_from
            run_expenses = TOTAL_WORKERS * case["worker_salary"] * tmod / 1440
            run_net_profit = run_revenue - run_expenses
            run_avg_time_service = d1.delta_t_service / d1.quantity if d1.quantity > 0 else float('inf')

            # Підсумок за всі прогони
            total_serviced_clients += run_serviced_clients
            total_unserviced_clients += run_unserviced_clients
            total_revenue += run_revenue
            total_net_profit += run_net_profit
            total_avg_time_service += run_avg_time_service

        # Розрахунок середніх значень
        avg_net_profit = total_net_profit / NUM_RUNS
        avg_avg_time_service = total_avg_time_service / NUM_RUNS
        avg_revenue = total_revenue / NUM_RUNS

        # Додавання результатів до таблиці
        results.append({
            "К-сть обслужених клієнтів": total_serviced_clients // NUM_RUNS,
            "К-сть не обслужених клієнтів": total_unserviced_clients // NUM_RUNS,
            "Час виконання замовлення (хв)": avg_avg_time_service,
            "Ціна 1го замовлення (в середньому)": avg_revenue / total_serviced_clients if total_serviced_clients > 0 else 0,
            "Чистий прибуток служби таксі (UAH)": avg_net_profit,
        })

        # Перетворення результатів у таблицю
    df = pd.DataFrame(results)
    print(df)

    # Збереження результатів у файл
    df.to_csv("taxi_service_results.csv", index=False)

