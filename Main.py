import argparse
import sys, os
import ruamel.yaml
from Graphs import BaseGraph, VMRkGraph, MNRkGraph, BaseTelNet, VMRkTelNet, MNRkTelNet

# TODO: реализовать оптимизацию графа по инк-нодам и дек-нодам для поиска конфигурации с наибольшим количеством
#  путей с конкретной достижимостью

# TODO: Сделать везде repr через additions.Representation

# TODO: Переделать всю документацию!

# TODO: Сделать все хардкод-константы (значения по умолчанию в классах BaseNode, BaseNetwork, например) через config.py

# TODO: Реализовать джиттер с отрицательными значениями

# TODO: после 100% загрузки пропускная способность ведер должна уходить в 0 (отказ функционирования реализовать)

# TODO: отключение узлов при превышении нагрузки на узел -> динамический пересчет маршрутов потоков

from Networks import BaseNetwork, TBNetwork
from NetworksSupport import BaseReportAnalyzer


def get_graph(config: dict) -> BaseGraph:
    graph_type = config.get('type')
    if graph_type == 'standard':
        return BaseGraph(config)
    elif graph_type == 'vmrk':
        return VMRkGraph(config)
    elif graph_type == 'mnrk':
        return MNRkGraph(config)
    elif graph_type == 'telnet':
        return BaseTelNet(config)
    elif graph_type == 'vmrk_telnet':
        return VMRkTelNet(config)
    elif graph_type == 'mnrk_telnet':
        return MNRkTelNet(config)
    else:
        raise Exception('В конфигурационном файле объявлен неверный тип графа.')

def create_config():
    # TODO:
    #  Реализовать эту функцию
    """
    Функция, которая будет создавать конфигурационный файл по вводу пользователя
    :return:
    """
    ...
def create_traffic():
    # TODO:
    #  Реализовать эту функцию
    """
    Функция, которая будет создавать файл трафика по вводу пользователя
    :return:
    """
    ...

def get_yaml(path):
    with open(os.path.abspath(path), 'r', encoding='utf-8') as f:
        lines = f.readlines()
    config = ruamel.yaml.load('\n'.join(lines), Loader=ruamel.yaml.SafeLoader)
    return config


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_path')
    parser.add_argument('--traffic_path')
    return parser.parse_args(args)

def read_message(path):
    f = open(os.path.abspath(path), 'r', encoding='utf-8')
    message = f.read()
    f.close()
    return message


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    config = get_yaml(args.config_path)
    traffic_params = get_yaml(args.traffic_path)

    graph = get_graph(config.get('graph'))

    BN = BaseNetwork(graph=graph)

    for stream in traffic_params['streams'].values():
        BN.add_message_to_send(message=read_message(path=stream['message_path']),
                               sender=stream['sender'],
                               receiver=stream['receiver'],
                               packet_size=None if stream['packet_size'] == 'default' else int(stream['packet_size']),
                               protocol=stream['protocol'],
                               special=stream.get('special', None))

    base_traffic_report, base_maintenance_report = BN.send_messages(verbose=True)

    base_traffic_report.prepare()
    base_maintenance_report.prepare()
    base_maintenance_report.prepare_total()
    base_maintenance_report.prepare_general_info()


    A = BaseReportAnalyzer(base_maintenance_report)
    tb_params = A.simple_analysis()


    TBN = TBNetwork(graph=graph, tb_params=tb_params)

    for stream in traffic_params['streams'].values():
        TBN.add_message_to_send(message=read_message(path=stream['message_path']),
                                sender=stream['sender'],
                                receiver=stream['receiver'],
                                packet_size=None if stream['packet_size'] == 'default' else int(stream['packet_size']),
                                protocol=stream['protocol'],
                                special=stream.get('special', None))

    traffic_report, maintenance_report = TBN.send_messages(verbose=True)

    traffic_report.prepare()
    maintenance_report.prepare()
    maintenance_report.prepare_total()
    maintenance_report.prepare_general_info()

    1+1
    # quality_report = A.get_efforts_quality(base_traffic_report, traffic_report)
    # efficiency_report = A.get_efforts_efficiency(base_maintenance_report, maintenance_report)

    # pass
    # paths = graph.calculate(start='1', goal='14', k=1,  mass=190)
    # graph.draw_graph_with_paths(paths=paths)

    # drawer.run()