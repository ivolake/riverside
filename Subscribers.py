# import random
#
# import Networks
# import additions as adds
# from Packets import BasePacket
# from Paths import Path
# from Streams import TCPStream, BaseStream
# import operator as op
#
#
# class BaseSubscriber:
#     def __init__(self,
#                  net: 'Networks.BaseNetwork',
#                  vertex: str,
#                  **kwargs):
#         self.net = net
#         self.vertex = vertex
#
#         self.delay_between_packets = kwargs.get('delay', 0)
#
#         self.sent_packets = []
#         self.received_packets = []
#
#     def receive_packet(self, pkt):
#         self.received_packets.append(pkt)
#
#
#     def send_message(self, receiver: str, message: str):
#         raise NotImplementedError
#
#     def check_and_find_path(self, s: BaseStream):
#         paths = self.net.graph.calculate(start=s.start, goal=s.goal, mass=1)  # Пакет ВВ
#
#         if paths:
#             path = paths.get_shortest()
#         else:
#             raise Exception('Между отправителем и получателем не существует допустимых путей.')
#
#         path_found = False
#         i = 0
#         while (not path_found) and (i < len(paths)):
#             path = paths[i]
#             path_bandwidth = min([self.net.nodes_characteristics[v]['capacity'] for v in path])
#             capacity_problem = path_bandwidth < max(s.packets, key=op.attrgetter('size')).size
#
#             if not capacity_problem:
#                 path = paths[i]
#                 path_found = True
#             else:
#                 i += 1
#         if not path_found:
#             raise Exception(
#                 'Между отправителем и получателем не существует путей с узлами, обладающими достаточной пропускной способнотью.')
#         return path
#
# class TCPSubscriber(BaseSubscriber):
#     def __init__(self, net: 'Networks.BaseNetwork', vertex: str, **kwargs):
#
#         super().__init__(net, vertex, **kwargs)
#
#         self.retries = kwargs.get('retries', 5)
#
#     def send_message(self, receiver: BaseSubscriber, message):  # -> MessageSendingReport
#         # Пересылка пакетов идет как в TCP. То есть следующий отправляется после того, как был доставлен предыдущий.
#         #  Количество попыток повторной посылки ограничено.
#
#         start = self.vertex
#         goal = receiver.vertex
#
#         s = TCPStream(sender=start, goal=goal, message=message, packet_size=256)
#
#         path = self.check_and_find_path(s=s)
#
#         time = 0  # Вычисление, сколько сообщение будет идти до адресата
#         received_message = ''  # Вычисление, каким сообщение дойдет до адресата
#         for pkt in s.packets:
#             sender = path.start
#             if self.net.nodes_characteristics[sender]['capacity'] < pkt.size:
#                 raise Exception(
#                     f'Узел {sender} (стартовый) обладает недостаточной пропускной способностью для отправки пакета {pkt.headings.get("id")}')
#             else:
#                 received_pkt_data = pkt.data
#
#                 pkt_time = pkt.size / (self.net.nodes_characteristics[sender]['processing_speed'] +
#                                        self.net.nodes_characteristics[sender]['jitter_f']())
#                 if random.randint(0, 100) < self.net.nodes_characteristics[sender]['distortion_probability']:
#                     received_pkt_data = adds.information_distortion(received_pkt_data,
#                                                                     dist_level=self.net.nodes_characteristics[sender]
#                                                                     ['distortion_level'])
#
#                 prev_vertex = sender
#                 for vertex in path[1:]:
#                     if self.net.nodes_characteristics[vertex]['capacity'] < pkt.size:
#                         raise Exception(f'Узел {vertex} обладает недостаточной пропускной способностью')
#                     else:
#                         pkt_time += pkt.size / self.net.graph.edges[(prev_vertex, vertex)] + \
#                                     pkt.size / (self.net.nodes_characteristics[vertex]['processing_speed'] +
#                                                 self.net.nodes_characteristics[vertex]['jitter_f']())
#                         if random.randint(0, 100) < self.net.nodes_characteristics[vertex]['distortion_probability']:
#                             received_pkt_data = adds.information_distortion(received_pkt_data,
#                                                                             dist_level=
#                                                                             self.net.nodes_characteristics[vertex][
#                                                                                 'distortion_level'])
#                         prev_vertex = vertex
#             time += pkt_time
#             received_message += received_pkt_data
#
#         return time, received_message
#
#
