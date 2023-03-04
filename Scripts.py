import os

from Networks import BaseNetwork, TBNetwork
from NetworksSupport import BaseReportAnalyzer
from general import get_graph


def script_1(config,
             traffic_params,
             experiment_params):
    graph = get_graph(config.get('graph'))
    experiment_name = experiment_params['name']
    experiment_reports_path = experiment_params['reports_path']

    BN = BaseNetwork(graph=graph)
    BN.add_traffic_to_send(traffic_params=traffic_params)
    base_traffic_report, base_maintenance_report = BN.send_messages(verbose=True)
    base_traffic_report.prepare()
    base_maintenance_report.prepare()
    base_maintenance_report.prepare_total()
    base_maintenance_report.prepare_general_info()

    A = BaseReportAnalyzer(base_maintenance_report)
    tb_params = A.simple_analysis_few_nodes(n=2)

    TBN = TBNetwork(graph=graph, tb_params=tb_params)
    TBN.add_traffic_to_send(traffic_params=traffic_params)
    traffic_report, maintenance_report = TBN.send_messages(verbose=True)
    traffic_report.prepare()
    maintenance_report.prepare()
    maintenance_report.prepare_total()
    maintenance_report.prepare_general_info()



    if not os.path.isdir(experiment_reports_path):
        os.mkdir(experiment_reports_path)
    base_traffic_report.save_to_txt(os.path.join(experiment_reports_path, f'base_traffic_report_test_{experiment_name}.json'))
    base_maintenance_report.save_to_txt(os.path.join(experiment_reports_path, f'base_maintenance_report_test_{experiment_name}.json'))
    traffic_report.save_to_txt(os.path.join(experiment_reports_path, f'traffic_report_test_{experiment_name}.json'))
    maintenance_report.save_to_txt(os.path.join(experiment_reports_path, f'maintenance_report_test_{experiment_name}.json'))


def script_2(config,
             traffic_params,
             experiment_params):
    ...
