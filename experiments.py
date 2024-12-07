from create import Create
from dispose import Dispose
from process import Process
from model import Model

NUM_RUNS = 20
def find_optimal_model():
    TOTAL_WORKERS = 15
    results = []
    tmod = 5440

    for operators in range(1, TOTAL_WORKERS):  # Перебір від 1 до 14 операторів
        taxis = TOTAL_WORKERS - operators  # Водії таксі = загальна кількість - оператори
        print(f"Simulating with {operators} operators and {taxis} taxis...")

        total_net_profit = 0
        total_avg_time_service = 0

        for run in range(NUM_RUNS):
            creator = Create(name='Call Generator', delay_mean=180 / 60, delay_dev=2, distribution='erlang')
            call_process = Process(name='Operators', delay_mean=3, distribution='exp', n_channel=operators, max_queue=0)
            dialing_processor = Process(name='Dialing', delay_mean=60 / 60, distribution='exp', max_queue=float('inf'))
            taxi_dispatch = Process(name='Taxis', delay_mean=40, delay_dev=10, distribution='uniform',
                                    n_channel=taxis, max_queue=10)
            d1 = Dispose(name='EXIT1')

            # Ланцюг зв'язків
            creator.next_element = [dialing_processor]
            dialing_processor.next_element = [call_process]
            call_process.next_element = [taxi_dispatch, dialing_processor]
            call_process.priority = [2, 1]
            taxi_dispatch.next_element = [d1]

            # Запуск моделі
            elements = [creator, dialing_processor, call_process, taxi_dispatch, d1]
            model = Model(elements, transition_period=4000)
            model.simulate(tmod)  # 1 день роботи (1440 хв)

            # Результати прогону
            total_revenue = 20 * d1.quantity + 3 * d1.total_distance_from
            total_expenses = TOTAL_WORKERS * 1000 * tmod / 1440

            net_profit = total_revenue - total_expenses
            avg_time_service = d1.delta_t_service / d1.quantity if d1.quantity > 0 else float('inf')

            total_net_profit += net_profit
            total_avg_time_service += avg_time_service

        # Розрахунок середніх значень
        avg_net_profit = total_net_profit / NUM_RUNS
        avg_avg_time_service = total_avg_time_service / NUM_RUNS

        # Збереження результатів
        results.append({
            'operators': operators,
            'taxis': taxis,
            'net_profit': avg_net_profit,
            'avg_time_service': avg_avg_time_service,
        })

    # Аналіз результатів
    optimal_time = min(results, key=lambda x: x['avg_time_service'])
    optimal_profit = max(results, key=lambda x: x['net_profit'])

    print("\nOptimal configuration to minimize service time:")
    print(f"  Operators: {optimal_time['operators']}, Taxis: {optimal_time['taxis']}")
    print(f"  Average Service Time: {optimal_time['avg_time_service']:.2f} minutes")

    print("\nOptimal configuration to maximize net profit:")
    print(f"  Operators: {optimal_profit['operators']}, Taxis: {optimal_profit['taxis']}")
    print(f"  Net Profit: {optimal_profit['net_profit']:.2f} UAH")


def create_model(drivers=10, max_queue=10, transition_period=None):
    TAXIS = drivers
    OPERATORS = 15 - TAXIS

    creator = Create(name='Call Generator', delay_mean=180 / 60, delay_dev=2, distribution='erlang')
    call_process = Process(name='Operators', delay_mean=3, distribution='exp', n_channel=OPERATORS, max_queue=0)
    dialing_processor = Process(name='Dialing', delay_mean=60 / 60, distribution='exp', max_queue=float('inf'))
    taxi_dispatch = Process(name='Taxis', delay_mean=40, delay_dev=10, distribution='uniform',
                            n_channel=TAXIS, max_queue=max_queue)
    d1 = Dispose(name='EXIT1')

    # Ланцюг зв'язків
    creator.next_element = [dialing_processor]
    dialing_processor.next_element = [call_process]
    call_process.next_element = [taxi_dispatch, dialing_processor]
    call_process.priority = [2, 1]
    taxi_dispatch.next_element = [d1]

    # Запуск моделі
    elements = [creator, dialing_processor, call_process, taxi_dispatch, d1]
    model = Model(elements, transition_period)
    return model


import numpy as np


import scipy.stats



def experimental_research():
    y_means = []
    residual_influence = 0
    SIM_TIME = 5440

    # Досліджувані фактори: кількість водіїв і максимальний розмір черги
    drivers_levels = [5, 10]  # Кількість водіїв
    queue_levels = [5, 10]  # Максимальний розмір черги на таксі

    results = []
    for drivers in drivers_levels:
        for max_queue in queue_levels:
            model_response = []
            for _ in range(NUM_RUNS):
                # Створення моделі з конкретними рівнями факторів
                model = create_model(drivers=drivers, max_queue=max_queue, transition_period=4000)
                model_response = model.simulate(SIM_TIME)

            print(f"\n------------- Результати симуляції (водії = {drivers}, черга = {max_queue}): -------------")
            print(f'Список значень відгуку: {model_response}')
            response_mean = sum(model_response) / len(model_response)
            print(f'Середнє значення відгуку: {response_mean}')
            y_means.append(response_mean)
            results.append((drivers, max_queue, response_mean))

            residual_influence += sum((value - response_mean) ** 2 for value in model_response)

    # Розрахунок впливу факторів
    y_mean = sum(y_means) / len(y_means)
    print(f'\n\ny_mean = {y_mean}')

    # Вплив кількості водіїв
    factor_drivers_influence = NUM_RUNS * len(queue_levels) * sum(
        (sum(y_means[i:i + len(queue_levels)]) / len(queue_levels) - y_mean) ** 2 for i in
        range(0, len(y_means), len(queue_levels))
    )

    # Вплив розміру черги
    factor_queue_influence = NUM_RUNS * len(drivers_levels) * sum(
        (sum(y_means[i::len(queue_levels)]) / len(drivers_levels) - y_mean) ** 2 for i in range(len(queue_levels))
    )

    # Взаємодія факторів
    interaction_influence = NUM_RUNS * sum(
        (response_mean - y_mean) ** 2 for _, _, response_mean in results
    ) - factor_drivers_influence - factor_queue_influence

    print(f'S_водіїв = {factor_drivers_influence}')
    print(f'S_черга = {factor_queue_influence}')
    print(f'S_взаємодія = {interaction_influence}')
    print(f'S_залиш = {residual_influence}')

    # Дисперсії
    factor_drivers_dispersion = factor_drivers_influence / (len(drivers_levels) - 1)
    factor_queue_dispersion = factor_queue_influence / (len(queue_levels) - 1)
    interaction_dispersion = interaction_influence / ((len(drivers_levels) - 1) * (len(queue_levels) - 1))
    residual_dispersion = residual_influence / (len(drivers_levels) * len(queue_levels) * (NUM_RUNS - 1))

    print(f'd_водіїв = {factor_drivers_dispersion}')
    print(f'd_черга = {factor_queue_dispersion}')
    print(f'd_взаємодія = {interaction_dispersion}')
    print(f'd_залиш = {residual_dispersion}')

    # Розрахунок критеріїв Фішера
    fisher_drivers = factor_drivers_dispersion / residual_dispersion
    fisher_queue = factor_queue_dispersion / residual_dispersion
    fisher_interaction = interaction_dispersion / residual_dispersion

    fisher_critical = scipy.stats.f.ppf(q=1 - .05, dfn=(len(drivers_levels) - 1),
                                        dfd=(len(drivers_levels) * len(queue_levels) * (NUM_RUNS - 1)))

    print(f'F_водіїв = {fisher_drivers}')
    print(f'F_черга = {fisher_queue}')
    print(f'F_взаємодія = {fisher_interaction}')
    print(f'F_кр = {fisher_critical}')

    # Аналіз значущості
    print("\nВисновки:")
    if fisher_drivers > fisher_critical:
        print("Фактор 'кількість водіїв' є значущим.")
    else:
        print("Фактор 'кількість водіїв' не є значущим.")

    if fisher_queue > fisher_critical:
        print("Фактор 'розмір черги' є значущим.")
    else:
        print("Фактор 'розмір черги' не є значущим.")

    if fisher_interaction > fisher_critical:
        print("Взаємодія факторів є значущою.")
    else:
        print("Взаємодія факторів не є значущою.")



if __name__ == "__main__":
    experimental_research()
    # find_optimal_model()
