# import random
#
# import Networks
# import additions as adds
# from Packets import BasePacket
# from Paths import Path
# import operator as op
#
# class BaseOperator:
#     def __init__(self, net: 'Networks.BaseNetwork', **kwargs):
#         self.net = net
#
#     def send_packet(self, pkt: BasePacket, path: Path):
#         sender = path.start
#
#         # Отправка пакета получателю
#         time = 0  # Вычисление, сколько сообщение будет идти до адресата
#         received_message = ''  # Вычисление, каким сообщение дойдет до адресата
#         if self.net.nodes_characteristics[sender]['capacity'] < pkt.size:
#             raise Exception(
#                 f'Узел {sender} (стартовый) обладает недостаточной пропускной способностью для отправки пакета {pkt.headings.get("id")}')
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
#                                                                         dist_level=self.net.nodes_characteristics[vertex]['distortion_level'])
#                     prev_vertex = vertex
#             time += pkt_time
#             received_message += received_pkt_data
#
#         return time, received_message
#
