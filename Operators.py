import random

import Networks
import additions as adds
from Streams import ConsistentStream, BaseStream
import operator as op


class BaseOperator:
    def __init__(self, net: 'Networks.BaseNetwork', **kwargs):
        self.net = net
        self.delay_between_packets = kwargs.get('delay', 0)

    def send_message(self, sender: str, receiver: str, message: str):  # -> ReceivedMessageReport
        if self.net.transmission_type == 'consistent':
            return self._send_message_consistently(sender=sender, receiver=receiver, message=message)
        elif self.net.transmission_type == 'simultaneous':
            return self._send_message_simultaneously(sender=sender, receiver=receiver, message=message)

    def _send_message_consistently(self, sender: str, receiver: str, message: str):  # -> ReceivedMessageReport
        #  Пересылка пакетов идет последовательно

        s = ConsistentStream(start=sender, goal=receiver, message=message, packet_size=256)

        path = self.check_and_find_path(s=s)

        time = 0
        received_message = ''
        for pkt in s.packets:
            if self.net.nodes_characteristics[sender]['capacity'] < pkt.size:
                raise Exception(f'Узел {sender} (стартовый) обладает недостаточной пропускной способностью')
            else:
                received_pkt_data = pkt.data

                pkt_time = pkt.size / (self.net.nodes_characteristics[sender]['processing_speed'] +
                                       self.net.nodes_characteristics[sender]['jitter_f']())
                if random.randint(0, 100) < self.net.nodes_characteristics[sender]['distortion_probability']:
                    received_pkt_data = adds.information_distortion(received_pkt_data,
                                                                    dist_level=self.net.nodes_characteristics[sender]
                                                                    ['distortion_level'])

                prev_vertex = sender
                for vertex in path[1:]:
                    if self.net.nodes_characteristics[vertex]['capacity'] < pkt.size:
                        raise Exception(f'Узел {vertex} обладает недостаточной пропускной способностью')
                    else:
                        pkt_time += pkt.size / self.net.graph.edges[(prev_vertex, vertex)] + \
                                    pkt.size / (self.net.nodes_characteristics[vertex]['processing_speed'] +
                                                self.net.nodes_characteristics[vertex]['jitter_f']())
                        if random.randint(0, 100) < self.net.nodes_characteristics[vertex]['distortion_probability']:
                            received_pkt_data = adds.information_distortion(received_pkt_data,
                                                                            dist_level=self.net.nodes_characteristics[vertex]
                                                                            ['distortion_level'])
                        prev_vertex = vertex
                time += pkt_time
                received_message += received_pkt_data

        return time, received_message

    # def _send_message_simultaneously(self, sender: str, receiver: str, message: str):  # -> ReceivedMessageReport
    #     #  Пересылка пакетов идет последовательно
    #
    #     s = ConsistentStream(start=sender, goal=receiver, message=message, packet_size=256)
    #
    #     paths = self.net.graph.calculate(start=s.start, goal=s.goal, mass=1)  # Пакет ВВ
    #
    #     path_bandwidth = [(p, min([self.net.nodes_characteristics[v]['capacity'] for v in p])) for p in paths]
    #     path_bandwidth = sorted(path_bandwidth, key=op.itemgetter(1))
    #
    #     time = 0
    #     received_pkts = []
    #     for pkt in s.packets:
    #         if self.net.nodes_characteristics[sender]['capacity'] < pkt.size:
    #             raise Exception(f'Узел {sender} (стартовый) обладает недостаточной пропускной способностью')
    #         else:
    #             received_pkt_data = pkt.data
    #
    #             pkt_time = pkt.size / (self.net.nodes_characteristics[sender]['processing_speed'] +
    #                                    self.net.nodes_characteristics[sender]['jitter_f']())
    #             if random.randint(0, 100) < self.net.nodes_characteristics[sender]['distortion_probability']:
    #                 received_pkt_data = adds.information_distortion(received_pkt_data,
    #                                                                 dist_level=self.net.nodes_characteristics[sender]
    #                                                                 ['distortion_level'])
    #
    #             prev_vertex = sender
    #             for vertex in path[1:]:
    #                 if self.net.nodes_characteristics[vertex]['capacity'] < pkt.size:
    #                     raise Exception(f'Узел {vertex} обладает недостаточной пропускной способностью')
    #                 else:
    #                     pkt_time += pkt.size / self.net.graph.edges[(prev_vertex, vertex)] + \
    #                                 pkt.size / (self.net.nodes_characteristics[vertex]['processing_speed'] +
    #                                             self.net.nodes_characteristics[vertex]['jitter_f']())
    #                     if random.randint(0, 100) < self.net.nodes_characteristics[vertex]['distortion_probability']:
    #                         received_pkt_data = adds.information_distortion(received_pkt_data,
    #                                                                         dist_level=self.net.nodes_characteristics[vertex]
    #                                                                         ['distortion_level'])
    #                     prev_vertex = vertex
    #             time += pkt_time
    #             received_message += received_pkt_data
    #
    #     return time, received_message

    def check_and_find_path(self, s: BaseStream):
        paths = self.net.graph.calculate(start=s.start, goal=s.goal, mass=1)  # Пакет ВВ

        if paths:
            path = paths.get_shortest()
        else:
            raise Exception('Между отправителем и получателем не существует допустимых путей.')

        path_found = False
        i = 0
        while (not path_found) and (i < len(paths)):
            path = paths[i]
            path_bandwidth = min([self.net.nodes_characteristics[v]['capacity'] for v in path])
            capacity_problem = path_bandwidth < max(s.packets, key=op.attrgetter('size')).size

            if not capacity_problem:
                path = paths[i]
                path_found = True
            else:
                i += 1
        if not path_found:
            raise Exception(
                'Между отправителем и получателем не существует путей с узлами, обладающими достаточной пропускной способнотью.')
        return path
