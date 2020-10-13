import argparse
import sys
import ruamel.yaml
from Graphs import BaseGraph, VMRkGraph, MNRkGraph, BaseTelNet, VMRkTelNet, MNRkTelNet

# TODO: реализовать объект потока, расчет его времени;
#  добавить в тип графа то, как он обрабатывает пакеты в потоке - одновременно или последовательно

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
    elif graph_type == 'vmrk_tb_telnet':
        pass
    elif graph_type == 'mnrk_tb_telnet':
        pass
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

def get_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    config = ruamel.yaml.load('\n'.join(lines), Loader=ruamel.yaml.SafeLoader)
    return config


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_path')
    return parser.parse_args(args)


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    config = get_config(args.config_path)

    # TODO: 10.10.2020 - странные результаты, проверить
    graph = get_graph(config.get('graph'))
    pass
    paths = graph.calculate(start='1', goal='8', k=1)
    graph.draw_graph_with_paths(paths=paths, n=2, permutate_paths=True)

    # drawer.run()