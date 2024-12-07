from create import Create
from dispose import Dispose
from process import Process
from model import Model

NUM_ITER = 20
TRANSITION_PERIOD = 4000


import numpy as np

if __name__ == '__main__':
    OPERATORS = 2 
    TAXIS = 18
    NUM_ITER = 20  # Кількість прогонів

    # Ініціалізація для зберігання результатів
    aggregated_results = {key: [] for key in [
        "Надійшло клієнтів", "Обслуговано клієнтів", "Середня довжина черги", "Середній час обслуговування",
        "Загальний дохід", "Загальні витрати", "Чистий прибуток"
    ]}
    aggregated_results["Обслуговування операторами"] = {"Cереднє завантаження": [], "Кількість": [],
                                                        "Ймовірність відмови": []}
    aggregated_results["Обслуговування таксистами"] = {"Cереднє завантаження": [], "Кількість": [],
                                                       "Середня довжина черги": [], "Ймовірність відмови": []}

    for _ in range(NUM_ITER):
        # Побудова і запуск моделі
        creator = Create(name='Call Generator', delay_mean=180 / 60, delay_dev=2, distribution='erlang')
        call_process = Process(name='Operators', delay_mean=3, distribution='exp', n_channel=OPERATORS, max_queue=0)
        dialing_processor = Process(name='Dialing', delay_mean=60 / 60, distribution='exp', max_queue=float('inf'))
        taxi_dispatch = Process(name='Taxis', delay_mean=40, delay_dev=10, distribution='uniform',
                                n_channel=TAXIS, max_queue=10)
        d1 = Dispose(name='EXIT1')

        creator.next_element = [dialing_processor]
        dialing_processor.next_element = [call_process]
        call_process.next_element = [taxi_dispatch, dialing_processor]
        call_process.priority = [2, 1]
        taxi_dispatch.next_element = [d1]

        elements = [creator, dialing_processor, call_process, taxi_dispatch, d1]
        model = Model(elements, transition_period=4000)
        model.simulate(5440)  # 1 день роботи
        result = model.print_result()

        # Агрегація результатів
        for key in aggregated_results:
            if isinstance(aggregated_results[key], dict):  # Для вкладених даних
                for sub_key in aggregated_results[key]:
                    aggregated_results[key][sub_key].append(result[key][sub_key])
            else:
                aggregated_results[key].append(result[key])

    # Обчислення середніх значень
    mean_results = {key: (
        {sub_key: np.mean(values) for sub_key, values in value.items()}
        if isinstance(value, dict) else np.mean(value)
    ) for key, value in aggregated_results.items()}

    # Форматований вивід результатів
    print("\n--- Середні результати за 20 прогонів ---\n")
    for key, value in mean_results.items():
        if isinstance(value, dict):  # Для вкладених результатів
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value:.4f}")
        else:
            print(f"{key}: {value:.4f}")
