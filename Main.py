import argparse
import sys
import ruamel.yaml
from functions import get_graph



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