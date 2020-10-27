import random

from Graphs import BaseGraph
from NetworksSupport import RandomJitter


# TODO: В kwargs передавать параметры для джиттер-функции и всего остального
from Operators import BaseOperator


class BaseNetwork:
    def __init__(self, graph: BaseGraph, **kwargs):
        self.graph = graph
        self.transmission_type = self.graph.config.get('transmission', None)

        if self.transmission_type is None:
            raise ValueError('В конфигурационном файле не определен способ передачи данных по сети (параметр "transmission").')

        self.nodes = self.graph.nodes

        tmpnc = {}
        for n in self.nodes:
            jitter_f = RandomJitter(0, 4, 5, 7, accuracy=5)
            tmpnc.update(
                {n: {'capacity': random.randrange(1000, 10000),
                     'processing_speed': random.randrange(1, 1000),
                     'jitter_f': jitter_f,
                     'distortion_probability': random.randint(0, 100),
                     'distortion_level': random.randint(0, 5)
                     }})

        self.nodes_characteristics = tmpnc

    def __repr__(self):
        return f'BaseNetwork(graph.type={self.graph.type}, graph.nodes={self.graph.nodes}, transmission_type={self.transmission_type})'

    @property
    def operator(self):
        return ConsistentOperator(net=self)

    def send_message(self, sender: str, receiver: str, message: str):
        return self.operator.send_message(sender=sender, receiver=receiver, message=message)
