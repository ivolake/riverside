import argparse
import sys
import ruamel.yaml



def get_config(path):
    with open(path, 'r') as f:
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

    calculator = Calculator(config)
    drawer = Drawer()
    calculator.run()
    drawer.run()