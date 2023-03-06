import sys
import os

from Scripts import *
from general import parse_args, get_yaml

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
    model_path = r'D:\OneDrive\Documents\Python_Scripts\Networks_Science_2\models\model1.yaml'
    model = get_yaml(model_path)
    network_path = model['network']  # args.config_path
    traffic_path = model['traffic']  # args.traffic_path
    network_params = get_yaml(network_path)
    traffic_params = get_yaml(traffic_path)

    _en = '6'
    experiment_params = {
        'name': _en,
        'reports_path': os.path.abspath(f'D:\\OneDrive\\Documents\\Научная работа\\Научная работа лето 3-4 курс 2020, осень 5 курс 2021\\Тесты\\Тест_{_en}\\')
    }

    # script_1(config,
    #          traffic_params,
    #          experiment_params)

    script_2(network_params,
             traffic_params,
             experiment_params)

    # 1+1
    # quality_report = A.get_efforts_quality(base_traffic_report, traffic_report)
    # efficiency_report = A.get_efforts_efficiency(base_maintenance_report, maintenance_report)

    # pass
    # paths = graph.calculate(start='1', goal='14', k=1,  mass=190)
    # graph.draw_graph_with_paths(paths=paths)

    # drawer.run()
