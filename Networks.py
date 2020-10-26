import random
import string

from Graphs import BaseGraph
from NetworksSupport import RandomJitter


# TODO: В kwargs передавать параметры для джиттер-функции
from Streams import BaseStream


class BaseNetwork:
    def __init__(self, graph: BaseGraph, **kwargs):
        self.graph = graph

        self.nodes = self.graph.nodes

    @property
    def nodes_characteristics(self):
        nodes_characteristics = {}
        for n in self.nodes:
            jitter_f = RandomJitter(0, 4, 5, 7, accuracy=5)
            nodes_characteristics.update(
                {n: {'processing_speed': random.randrange(0, 1000) / 100,
                     'jitter_f': jitter_f,
                     'distortion_probability': random.randint(0, 100),
                     'distortion_level': random.randint(0, 5)
                     }})
        return nodes_characteristics

    def _ID_random_insertion(self, info):
        """
        ID - Information Distortion
        Операция по случайной вставке
        Parameters
        ----------
        info

        Returns
        -------

        """
        i = random.randint(0, len(info))
        return info[0:i] + random.choice(string.printable[:-2]) + info[i:]

    def _ID_random_deletion(self, info):
        """
        ID - Information Distortion
        Операция по случайному удалению
        Parameters
        ----------
        info

        Returns
        -------

        """
        i = random.randint(0, len(info))
        return info[0:i] + info[i+1:]

    def _ID_random_substitution(self, info):
        """
        ID - Information Distortion
        Операция по случайной замене
        Parameters
        ----------
        info

        Returns
        -------

        """
        i = random.randint(0, len(info))
        return info[0:i] + random.choice(string.printable[:-2]) + info[i+1:]


    def information_distortion(self, info: str, dist_level: int = 1):
        distorted = info
        for i in range(0, dist_level):
            distorted = random.choice([self._ID_random_insertion,
                                       self._ID_random_deletion,
                                       self._ID_random_substitution])(distorted)
        return distorted

# TODO: Вынести отправку в отдельный sender?..
    def send_message(self, sender: str, receiver: str, message: str): #  -> ReceivedMessageReport
        #  Пересылка пакетов идет последовательно

        s = BaseStream(start=sender, goal=receiver, message=message, packet_size=256)

        paths = self.graph.calculate(start=sender, goal=receiver, mass=1) # Пакет ВВ

        if paths:
            path = paths.get_shortest()
        else:
            raise Exception('Между отправителем и получателем не существует приемлемых путей.')

        time = 0
        received_message = ''
        for pkt in s.packets:
            pkt_time = pkt.size / (self.nodes_characteristics[sender]['processing_speed'] +
                               self.nodes_characteristics[sender]['jitter_f']())

            received_pkt_data = pkt.data
            prev_vertex = sender
            for vertex in path[1:]:
                pkt_time += pkt.size / self.graph.edges[(prev_vertex, vertex)] + \
                        pkt.size / (self.nodes_characteristics[vertex]['processing_speed'] +
                               self.nodes_characteristics[vertex]['jitter_f']())
                if random.randint(0, 100) < self.nodes_characteristics[vertex]['distortion_probability']:
                    received_pkt_data = self.information_distortion(received_pkt_data,
                                                                    dist_level=self.nodes_characteristics[vertex]
                                                                    ['distortion_level'])
                prev_vertex = vertex
            time += pkt_time
            received_message += received_pkt_data

        return time, received_message
