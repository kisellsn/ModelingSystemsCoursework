from create import Create
from dispose import Dispose
from process import Process
from model import Model


if __name__ == '__main__':
    OPERATORS = 5
    TAXIS = 10

    creator = Create(name='Call Generator', delay_mean=180 / 60, delay_dev=2, distribution='erlang')
    call_process = Process(name='Operators', delay_mean=3, distribution='exp', n_channel=OPERATORS, max_queue=0)
    dialing_processor = Process(name='Dialing', delay_mean=60 / 60, distribution='exp', max_queue=float('inf'))
    taxi_dispatch = Process(name='Taxis', delay_mean=40, delay_dev=10, distribution='uniform',
                            n_channel=TAXIS, max_queue=10)
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
    model.simulate(1440)  # 1 день роботи
    # model.simulate(43200)  # місяць
