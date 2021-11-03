import argparse
import ruamel.yaml
import os

from Graphs import BaseGraph, VMRkGraph, MNRkGraph, BaseTelNet, VMRkTelNet, MNRkTelNet


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
