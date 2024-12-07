import matplotlib.pyplot as plt

from create import Create
from dispose import Dispose
from model import Model
from process import Process

SIM_TIME = 6000

if __name__ == "__main__":
    for _ in range(4):
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
        model_response = model.simulate(SIM_TIME)

        plt.plot(list(range(100, SIM_TIME, 100)), model_response[:len(range(100, SIM_TIME, 100))])
        plt.ylim(95, max(model_response)+5)
        plt.yticks(range(95, 120, 2))

    plt.title(f'Значення відгуку моделі в залежності від часу моделювання')
    plt.show()

