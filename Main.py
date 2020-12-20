import argparse
import sys
import ruamel.yaml
from Graphs import BaseGraph, VMRkGraph, MNRkGraph, BaseTelNet, VMRkTelNet, MNRkTelNet

# TODO: реализовать объект потока, расчет его времени;
#  добавить в тип графа то, как он обрабатывает пакеты в потоке - одновременно или последовательно
#  UPD: это будет в классе Сети

# TODO: Следующий уровень абстракции - на базе графа строится Сеть, и с ней могут взаимодействовать
#  Абоненты - т.е. отправлять и получать сообщения

# TODO: реализовать объект оператора, которому передается граф, и который имеет метод "послать поток по графу"

# TODO: реализовать оптимизацию графа по инк-нодам и дек-нодам для поиска конфигурации с наибольшим количеством
#  путей с конкретной достижимостью

# TODO: Передача потока в "реальном времени", т.е. с учетом емкости и задержки обработки узлов - это разбиаение
#  маршрута на участки между нодами и подсчет на каждой итоговой нагрузки на ноду, прибавление ее задежрки и т.д.

# TODO: Сделать везде repr через additions.Representation!!!!!!!

# TODO: Переделать всю документацию!

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

    graph = get_graph(config.get('graph'))
    pass
    paths = graph.calculate(start='1', goal='14', k=1,  mass=190)
    graph.draw_graph_with_paths(paths=paths)

    # drawer.run()