import argparse
import sys
import ruamel.yaml
from Graphs import BaseGraph, VMRkGraph, MNRkGraph, BaseTelNet

def get_graph(config: dict) -> BaseGraph:
    graph_type = config.get('type')
    if graph_type == 'simple':
        return BaseGraph(config)
    elif graph_type == 'vmrk':
        return VMRkGraph(config)
    elif graph_type == 'mnrk':
        return MNRkGraph(config)
    elif graph_type == 'telnet':
        return BaseTelNet(config)
    elif graph_type == 'vmrk_telnet':
        pass
    elif graph_type == 'mnrk_telnet':
        pass
    elif graph_type == 'vmrk_tb_telnet':
        pass
    elif graph_type == 'mnrk_tb_telnet':
        pass
    else:
        raise Exception('Wrong graph type declared in config')


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

    graph = get_graph(config.get('graph'))
    pass
    # calculator = Calculator(config)
    # drawer = Drawer()
    # calculator.run()
    # drawer.run()