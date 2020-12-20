import random
import operator as op

from Graphs import BaseGraph
from NetworksSupport import Traffic
from Nodes import BaseNode
from Streams import BaseStream


# TODO: В kwargs передавать параметры для джиттер-функции и всего остального

class BaseNetwork:
    def __init__(self, graph: BaseGraph, **kwargs):
        self.graph = graph
        self.protocol = self.graph.config.get('protocol', None)

        self.TCP_timeout = kwargs.get('TCP_timeout', 20)
        self.TCP_attempts_limit = kwargs.get('TCP_attempts_limit', 5)

        if self.protocol is None:
            raise ValueError('В конфигурационном файле не определен способ передачи данных по сети (параметр "transmission").')

        self.nodes = {}
        for n in self.graph.nodes:
            self.nodes.update({n: BaseNode(nodeid=n,
                                           capacity=random.randrange(1000, 10000),
                                           processing_speed=random.randrange(1, 1000),
                                           distortion_probability=random.randint(0, 100),
                                           distortion_level= random.randint(0, 5)
                                           )})


    def __repr__(self):
        return f'BaseNetwork(graph.type={self.graph.type}, graph.nodes={self.graph.nodes}, protocol={self.protocol})'

    # для TCP
    def check_and_find_path(self, s: BaseStream):
        paths = self.graph.calculate(start=s.sender, goal=s.receiver, mass=1)  # Пакет ВВ

        if paths:
            path = paths.get_shortest()
        else:
            raise Exception('Между отправителем и получателем не существует допустимых путей.')

        path_found = False
        i = 0
        while (not path_found) and (i < len(paths)):
            path = paths[i]
            path_bandwidth = min([self.nodes[v].capacity for v in path])
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

    # для UDP
    def check_and_find_all_paths(self, s: BaseStream):
        paths = self.graph.calculate(start=s.sender, goal=s.receiver, mass=1)  # Пакет ВВ

        if paths:
            paths.get_shortest()
        else:
            raise Exception('Между отправителем и получателем не существует допустимых путей.')

        paths_found = type(paths)([]) # создать истанс такой же коллекции путей, что и была передана в paths
        for path in paths:
            path_bandwidth = min([self.nodes[v].capacity for v in path])

            capacity_problem = path_bandwidth < max(s.packets, key=op.attrgetter('size')).size

            if not capacity_problem:
                paths_found.append(path)

        if not paths_found:
            raise Exception(
                'Между отправителем и получателем не существует путей с узлами, обладающими достаточной пропускной способнотью.')

        return paths_found

    def start_traffic(self, traffic: Traffic):  # -> MessageSendingReport
        # if self.protocol == 'TCP':
        #     subscriberA = TCPSubscriber(net=self, vertex=sender)
        #     subscriberB = TCPSubscriber(net=self, vertex=receiver)
        # else:
        #     subscriberA = UDPSubscriber(net=self, vertex=sender)
        #     subscriberB = UDPSubscriber(net=self, vertex=receiver)
        #
        # result = subscriberA.send_message(receiver=subscriberB, message=message)


        operating_memory = {}
        for s in traffic:
            operating_memory.update({s.id: {}})
            paths = self.check_and_find_all_paths(s=s)
            stream_data = {
                'stream': s,
                'paths': paths,
                'shortest_path': paths.get_shortest(),
                'time': 0,
                'received_data': ''
            }

            operating_memory[s.id] = stream_data


        all_messages_delivered = False
        while not all_messages_delivered:
            all_messages_delivered = True
            # дальше при итерировании по вершинам этот флаг обернется в False, если хоть
            #  на какой-то вершине у какого-либо пакета ((receiver != название вершины) или (next_hop не пустой))

            popped_packets = traffic.pop_packets()

            # установить новый next_hop пакетам ...

            for node in self.nodes:
                ...
                for packet in node.queue:
                    if packet.next_hop != '':
                        all_messages_delivered = False

                    if packet.protocol == 'TCP':
                        if packet.start_node == node.id
                    elif packet.protocol == 'UDP':
                        ...
                    else:
                        e = Exception(f'Протокол пакета (id: {packet.id}) не распознан ({packet.protocol})')
                        print(e)


                    # Info: перемещение пакетов происходит следующим образом:
                    #  1) Проверка выполнения условий для перемещения конкретно этого пакета
                    #  2) Если они выполнены, то его текущий next_hop запоминается в отдельную переменную.
                    #  3) Из operating_memory подтягивается название (id) следующего (следующего после запомненного
                    #     next_hop) узла, которому становится равным next_hop пакета.
                    #  4) У пакета меняется travel_time на величину, равную сумме времени на обработку в текущем узле и
                    #     времени, которое будет затрачено на путь до следующего узла.
                    #  5) Пакет удаляется из очереди текущего узла и добавляется в очередь следующего.
                    #
                    # Проверка неотправленных пакетов в каждой вершине:
                    #
                    #  Если next_hop у какого-либо пакета не пустой, то all_messages_delivered = False
                    #  (У всех пакетов будет пустой next_hop, когда они все дойдут до своих оконечных узлов, где их next_hop будет очищен)
                    # <<<---------------------------
                    #
                    #  Сначала на Протокол: tcp или udp
                    #  Если tcp, то:
                    #   Для стартового узла (при переборе пакетов в узле идет сравнение со start_node):
                    #    Info: при отсылании пакетов со стартовой ноды они перемещаются в список ожидающих подтверждения прибытия (node.awaiting_dict)
                    #
                    #    Проверка пакетов флаг received_answer на пакете, который означает, что ответ на предыдущий пакет был получен.
                    #     Условие установки флага received_answer - наличие на одной и той же ноде пакета с определенным pid и
                    #     флагом is_answer=False и пакета с is_answer=True и parent_pid=pid этого пакета
                    #    Если флаг received_answer=True, то:
                    #     Проверить, пришел ли вовремя ответ, сравнив travel_time пакета-ответа с self.TCP_timeout
                    #     Если ответ пришел вовремя (travel_time пакета-ответа < self.TCP_timeout) и (sending_attempts < self.TCP_attempts_limit), то
                    #      Переместить пакет на следующий узел (указан в заголовке этого пакета в параметре 'next_hop'). Пакет-ответ удалить.
                    #     Если ответ опоздал:
                    #      Увеличить sending_attempts на 1 и отослать предыдущий пакет заново на узел-receiver. Предыдущий
                    #      пакет лежит в node.awaiting_dict и остается там, пока не придет положительный ответ, либо не
                    #      истечет количество попыток. После истечения количества повторных попыток предыдущий пакет просто
                    #      удаляется и происходит отправка текущего пакета (путем установления received_answer в True).
                    #   Для промежуточного узла:
                    #    Просто передача в next_hop
                    #
                    #   Для оконечного узла (при переборе пакетов в узле идет сравнение со goal_node):
                    #    Проверка флага is_answer:
                    #     Если False:
                    #      Проверка на то, новый ли этот пакет на данном узле (непустой next_hop):
                    #       Если True:
                    #        Создать пакет-ответ о получении прибывшего пакета. Путь - такой же, как у прибывшего. Переместить пакет-ответ сразу в next_hop.
                    #        Сделать пустым next_hop у прибывшего пакета.
                    #       Если False:
                    #        Ничего не делать.
                    #     Если True:
                    #      Пакет перемещается next_hop (можно частично объединить с False-сценарием).
                    #      (Этот случай возможен, только если пакет-ответ был сгенерирован не здесь).
                    #
                    #  Если udp, то:
                    #
                    #   Для стартового узла (при переборе пакетов в узле идет сравнение со start_node):
                    #    Просто передача в next_hop
                    #
                    #
                    #
                    #
                    #   Для промежуточного узла:
                    #    Просто передача в next_hop
                    #
                    #
                    #
                    #
                    #   Для оконечного узла (при переборе пакетов в узле идет сравнение со goal_node):
                    #    Всем пакетам установить next_hop='', если у каких-то он еще не пустой
                    #
                    #
                    #
                    #
                    #
                    #
                    #
                    #
                    #
                    #
                    #
                    #
                    #


                    # ИДЕЯ: ПРИ РЕАЛИЗАЦИИ АЛГОРИТМА ДЫРЯВОГО ВЕДРА НУЖНО УЧЕСТЬ, ЧТО ПАКЕТЫ-ОТВЕТЫ НЕ ДОЛЖНЫ ТЕРЯТЬСЯ
                    # ИДЕЯ: ВРЕМЯ ОБРАБОТКИ ПАКЕТА НА УЗЛЕ ЗАВИСИТ ОТ ЕГО ПОЛОЖЕНИЯ В ОЧЕРЕДИ




                # если в какой-то вершине ((у всех пакетов с каким-то sid пустой next_hop) и (у всех пакетов с каким-то sid receiver совпадает с именем вершины)), то
                #  обращаясь по этому sid, собрать у пакетов received message


        # for s in traffic:
        #     # s = TCPStream(start=start, goal=goal, message=message, packet_size=256)
        #
        #     start = s.start
        #     goal = s.goal
        #     path = self.check_and_find_path(s=s)
        #
        #     time = 0  # Вычисление, сколько сообщение будет идти до адресата
        #     received_message = ''  # Вычисление, каким сообщение дойдет до адресата
        #
        #     for node_name in path:


        return result

