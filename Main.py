import sys
import os

from Networks import BaseNetwork, TBNetwork
from NetworksSupport import BaseReportAnalyzer
from general import parse_args, get_yaml, get_graph, read_message


# TODO: реализовать оптимизацию графа по инк-нодам и дек-нодам для поиска конфигурации с наибольшим количеством
#  путей с конкретной достижимость
#  Поставленная проблема в терминах применения нестандартной достижимости как инструмента поиска узлов
#  копирования трафика сети: Как определить узлы, на которых будет происходить копирование так,
#  чтобы произвести наименьшие изменения сети? Под изменениями в данном случае понимается
#  добавление в узел аппаратуры клонирования трафика.

# TODO: Сделать везде repr через additions.Representation

# TODO: Переделать всю документацию!

# TODO: Сделать все хардкод-константы (значения по умолчанию в классах BaseNode, BaseNetwork, например) через config.py

# TODO: Реализовать джиттер с отрицательными значениями

# TODO: после 100% загрузки пропускная способность ведер должна уходить в 0 (отказ функционирования реализовать)

# TODO: отключение узлов при превышении нагрузки на узел -> динамический пересчет маршрутов потоков

# TODO: переименовать "конфиг-файл" (файл с описанием сети) в программе в "файл сети"

# TODO: Добавить возможность записывать в файл сети tb_params


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
    tb_params = A.simple_analysis_few_nodes(n=2)


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

    experiment_name = '4'
    tests_dir_path = os.path.abspath(f'D:\\OneDrive\\Documents\\Научная работа\\Научная работа лето 3-4 курс 2020, осень 5 курс 2021\\Тесты\\Тест_{experiment_name}\\')

    if not os.path.isdir(tests_dir_path):
        os.mkdir(tests_dir_path)
    base_traffic_report.save_to_txt(os.path.join(tests_dir_path, f'base_traffic_report_test_{experiment_name}.json'))
    base_maintenance_report.save_to_txt(os.path.join(tests_dir_path, f'base_maintenance_report_test_{experiment_name}.json'))
    traffic_report.save_to_txt(os.path.join(tests_dir_path, f'traffic_report_test_{experiment_name}.json'))
    maintenance_report.save_to_txt(os.path.join(tests_dir_path, f'maintenance_report_test_{experiment_name}.json'))

    # 1+1
    # quality_report = A.get_efforts_quality(base_traffic_report, traffic_report)
    # efficiency_report = A.get_efforts_efficiency(base_maintenance_report, maintenance_report)

    # pass
    # paths = graph.calculate(start='1', goal='14', k=1,  mass=190)
    # graph.draw_graph_with_paths(paths=paths)

    # drawer.run()
