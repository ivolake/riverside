import json
import os
from itertools import compress

from NetworksSupport import Traffic
import additions as adds

class BaseReport:
    def __init__(self):
        pass

    # def __getitem__(self, key):
    #     return NotImplemented
    #
    # def __setitem__(self, key, value):
    #     return NotImplemented

    def __len__(self):
        return NotImplemented

    def __repr__(self):
        return NotImplemented

    @property
    def status(self):
        """

        Returns
        -------
        Значение от 0 до 1. 0 - отчет не заполнен полностью, 1 - отчет готов.

        """

        return NotImplemented


    def prepare(self):
        """

        Returns
        -------
        Количество незаполненных метрик в следствие отсутствия необходимых данных
        """
        return NotImplemented

    def convert_to_excel(self):
        return NotImplemented

    def save_to_txt(self, file_path: str):
        return NotImplemented



class TrafficReport(BaseReport):
    def __init__(self, traffic: Traffic):

        super().__init__()

        self.__tid = traffic.id
        ids = [str(s.id) for s in traffic]

        reports = [{
            'protocol': s.protocol,
            'time': 0,
            'original': {
                'message': s.message,
                'message_size': s.size,
                'packages_count': len(s),
            },
            'received_packets': None,
            'received_data': {
                'message': None,
                'message_size': None,
                'packets_time': None,
            },
            'metrics': {
                'packages_loss': None,
                'message_len_loss': None,
                'message_size_loss': None,
                'messages_dl_dist': None,
                'messages_h_dist': None
            }
        } for s in traffic]

        self.__reports = dict(zip(ids, reports))

    def __getitem__(self, key):
        # return adds.get_vals_from_inherited_keys(self.__reports, key)
        return self.__reports[key]

    def __setitem__(self, key, value):
        # adds.set_vals_from_inherited_keys(self.__reports, key, value)
        self.__reports[key] = value

    def __len__(self):
        return len(self.__reports)

    def __repr__(self):
        return f'Report of Traffic object with ID {self.__tid}. Status: {self.status * 100}% / 100%'

    @property
    def tid(self):
        """
        Traffic id
        Returns
        -------

        """
        return self.__tid

    # @property
    # def reports(self):
    #     return self.__reports

    def keys(self):
        return self.__reports.keys()

    def values(self):
        return self.__reports.values()

    @property
    def status(self):
        """

        Returns
        -------
        Значение от 0 до 1. 0 - отчет не заполнен полностью, 1 - отчет готов.

        """
        report_done = 0

        for r in self.values():
            if r['received_packets'] is not None:
                report_done += len(r['received_packets']) / r['original']['packages_count']

        report_done /= len(self)
        return round(report_done, 4)

    def prepare(self):
        """

        Returns
        -------
        Количество незаполненных метрик в следствие отсутствия необходимых данных
        """
        unfilled_metrics = 0
        if not self.status:
            print('Отчет заполнен не всеми данными по трафику. Результат будет неполным.')
        for sid, r in self.__reports.items():
            if r['protocol'] == 'TCP':
                for p_time in r['received_data']['packets_time'].values():
                    r['time'] += p_time
            elif r['protocol'] == 'UDP':
                r['time'] = max(r['received_data']['packets_time'].values())
            else:
                raise Exception(f"Поток s.id={sid} имеет недопустимый протокол {r['protocol']}")

            orig_msg = r['original']['message']
            orig_msg_size = r['original']['message_size']
            orig_pkg_c = r['original']['packages_count']

            sorted_packets = sorted(r['received_packets'].values(), key=lambda x: int(x.pid)) # сортировка прибывших пакетов по их pid
            r['received_data']['message'] = ''.join([p.data for p in sorted_packets])
            r['received_data']['message_size'] = sum([p.size for p in sorted_packets])
            r['received_data']['packages_count'] = len(sorted_packets)

            rec_msg = r['received_data']['message']
            rec_msg_size = r['received_data']['message_size']
            rec_pkg_c = r['received_data']['packages_count']

            if orig_pkg_c is not None and rec_pkg_c is not None:
                r['metrics']['packages_loss'] = 1 - rec_pkg_c / orig_pkg_c
            else:
                unfilled_metrics += 1
            if orig_msg is not None and rec_msg is not None:
                r['metrics']['message_len_loss'] = 1 - len(rec_msg) / len(orig_msg)
            else:
                unfilled_metrics += 1
            if orig_msg_size is not None and rec_msg_size is not None:
                r['metrics']['message_size_loss'] = 1 - rec_msg_size / orig_msg_size
            else:
                unfilled_metrics += 1
            if orig_msg is not None and rec_msg is not None:
                r['metrics']['messages_dl_dist'] = adds.damerau_levenshtein_distance(rec_msg, orig_msg)
                r['metrics']['messages_h_dist'] = adds.huffman_distance(rec_msg, orig_msg)
            else:
                unfilled_metrics += 1

        return unfilled_metrics

    def show(self):
        reports = {}
        for k, v in self.__reports.items():
            new_v = dict(v, **v)
            new_v.pop('received_packets')
            reports.update({k: new_v})

        print(json.dumps(reports, indent=4, ensure_ascii=False))

    def convert_to_excel(self):
        return NotImplemented

    def save_to_txt(self, file_path: str):
        with open(os.path.abspath(file_path), 'w', encoding='utf-8') as f:
            _ = dict(self.__reports, **self.__reports)
            for i in _:
                _[i].pop('received_packets')
            s = json.dumps(_, indent=4, ensure_ascii=False)
            f.write(s)


# TODO: добавить расчеты метрик по скорости вершины (все то же самое). Но как получать данные по скорости?

class MaintenanceReport(BaseReport):
    def __init__(self, network):

        super().__init__()
        self.__nid = network.id

        self.__network = network

        ids = [str(n) for n in self.__network.nodes]

        reports = [{
            'id': node_id,
            'capacity': node.capacity,
            # 'processing_speed': node.processing_speed,
            'data_recorded': {
                'filled_space': None, # список
            },
            'metrics': {
                'filled_space': {
                    'average': None,
                    'median': None,
                    'min': None,
                    'max': None,
                },
                'filled_space_relative': {
                    'average': None,
                    'median': None,
                    'min': None,
                    'max': None,
                },
                'overfilled_space': {
                    'average': None,
                    'median': None,
                    'min': None,
                    'max': None,
                },
                'overfilled_space_relative': {
                    'average': None,
                    'median': None,
                    'min': None,
                    'max': None,
                },
            },
        } for node_id, node in self.__network.nodes.items()]

        self.__reports = dict(zip(ids, reports))

        self.__total = {
            'average_filled_space': {
                'average': None,
                'median': None,
                'min': None,
                'max': None,
            },
            'median_filled_space': {
                'average': None,
                'median': None,
                'min': None,
                'max': None,
            },
            'min_filled_space': {
                'average': None,
                'median': None,
                'min': None,
                'max': None,
            },
            'max_filled_space': {
                'average': None,
                'median': None,
                'min': None,
                'max': None,
            },
            'overfilled_nodes_count': {
                'average': None,
                'median': None,
                'min': None,
                'max': None,
            },
            'average_overfilled_space': {
                'average': None,
                'median': None,
                'min': None,
                'max': None,
            },
            'median_overfilled_space': {
                'average': None,
                'median': None,
                'min': None,
                'max': None,
            },
            'min_overfilled_space': {
                'average': None,
                'median': None,
                'min': None,
                'max': None,
            },
            'max_overfilled_space': {
                'average': None,
                'median': None,
                'min': None,
                'max': None,
            },
            'average_relative_overfilled_space': {
                'average': None,
                'median': None,
                'min': None,
                'max': None,
            },
            'median_relative_overfilled_space': {
                'average': None,
                'median': None,
                'min': None,
                'max': None,
            },
            'min_relative_overfilled_space': {
                'average': None,
                'median': None,
                'min': None,
                'max': None,
            },
            'max_relative_overfilled_space': {
                'average': None,
                'median': None,
                'min': None,
                'max': None,
            },
        }

        self.__general_info = {
            'max_filled_node': {
                'node_id': None,
                'metrics': None,
            },
            'min_filled_node': {
                'node_id': None,
                'metrics': None,
            },
            'overfilled_nodes_ids': None, # список

        }

    @property
    def nid(self):
        """
        Network id
        Returns
        -------

        """
        return self.__nid

    def __getitem__(self, key):
        # return adds.get_vals_from_inherited_keys(self.__reports, key)
        return self.__reports[key]

    def __setitem__(self, key, value):
        # adds.set_vals_from_inherited_keys(self.__reports, key, value)
        self.__reports[key] = value

    def __len__(self):
        return len(self.__reports)

    def __repr__(self):
        return f'Report of Network Maintenance object with ID {self.__nid}. Status: {self.status * 100}% / 100%'

    @property
    def status(self):
        """

        Returns
        -------
        Значение от 0 до 1. 0 - отчет не заполнен полностью, 1 - отчет готов.

        """
        metrics_done = 0
        metrics_total = 0

        for r in self.__reports.values():
            metrics = r['metrics']
            for submetrics in metrics.values():
                for metric in submetrics.values():
                    if metric is not None:
                        metrics_done += 1
                    metrics_total += 1

        for metrics in self.__total.values():
            for metric in metrics.values():
                if metric is not None:
                    metrics_done += 1
                metrics_total += 1

        for metrics in self.__general_info.values():
            if metrics is not None and isinstance(metrics, dict):
                for metric in metrics.values():
                    if metric is not None:
                        metrics_done += 1
                    metrics_total += 1
            elif metrics is not None and not isinstance(metrics, dict):
                metrics_done += 1
                metrics_total += 1
            else:
                metrics_total += 1


        return metrics_done / metrics_total

    @property
    def total(self):
        return self.__total

    @property
    def general_info(self):
        return self.__general_info

    def keys(self):
        return self.__reports.keys()

    def values(self):
        return self.__reports.values()

    # noinspection PyTypeChecker
    def prepare(self):
        network_capacity = 0
        reports_values = self.__reports.values()
        for r in reports_values:
            fs = r['data_recorded']['filled_space']
            fs_sum = sum(fs)
            fs_len = len(fs)

            r['metrics']['filled_space']['average'] = round(fs_sum / fs_len, 4)
            if fs_len % 2 == 0:
                r['metrics']['filled_space']['median'] = round(fs[int(fs_len / 2)], 4)
            else:
                r['metrics']['filled_space']['median'] = round((fs[int(fs_len / 2)] + fs[int(fs_len / 2) + 1]) / 2, 4)
            r['metrics']['filled_space']['min'] = min(fs)
            r['metrics']['filled_space']['max'] = max(fs)

            capacity = r['capacity']
            network_capacity += capacity
            fs_rel = [round(fs_record/capacity, 4) for fs_record in fs]
            fs_rel_sum = sum(fs_rel)
            fs_rel_len = len(fs_rel)

            r['metrics']['filled_space_relative']['average'] = round(fs_rel_sum / fs_rel_len, 4)
            if fs_len % 2 == 0:
                r['metrics']['filled_space_relative']['median'] = round(fs_rel[int(fs_rel_len / 2)], 4)
            else:
                r['metrics']['filled_space_relative']['median'] = round((fs_rel[int(fs_rel_len / 2)] + fs_rel[int(fs_rel_len / 2) + 1]) / 2, 4)
            r['metrics']['filled_space_relative']['min'] = min(fs_rel)
            r['metrics']['filled_space_relative']['max'] = max(fs_rel)

            ofs = [fs_record - capacity if fs_record > capacity else 0 for fs_record in fs]
            ofs = list(compress(ofs, ofs))
            ofs_sum = sum(ofs)
            ofs_len = len(ofs)

            if ofs_len != 0:
                r['metrics']['overfilled_space']['average'] = round(ofs_sum / ofs_len, 4)
                if fs_len % 2 == 0:
                    r['metrics']['overfilled_space']['median'] = round(ofs[int(ofs_len / 2)], 4)
                else:
                    r['metrics']['overfilled_space']['median'] = round((ofs[int(ofs_len / 2)] + ofs[int(ofs_len / 2) + 1]) / 2, 4)
                r['metrics']['overfilled_space']['min'] = min(ofs)
                r['metrics']['overfilled_space']['max'] = max(ofs)
            else:
                r['metrics']['overfilled_space']['average'] = 0
                r['metrics']['overfilled_space']['median'] = 0
                r['metrics']['overfilled_space']['min'] = 0
                r['metrics']['overfilled_space']['max'] = 0

            ofs_rel = [round((fs_record - capacity) / capacity, 4) if fs_record > capacity else 0 for fs_record in fs]
            ofs_rel = list(compress(ofs_rel, ofs_rel))
            ofs_rel_sum = sum(ofs_rel)
            ofs_rel_len = len(ofs_rel)

            if ofs_rel_len != 0:
                r['metrics']['overfilled_space_relative']['average'] = round(ofs_rel_sum / ofs_rel_len, 4)
                if fs_len % 2 == 0:
                    r['metrics']['overfilled_space_relative']['median'] = round(ofs_rel[int(ofs_rel_len / 2)], 4)
                else:
                    r['metrics']['overfilled_space_relative']['median'] = round((ofs_rel[int(ofs_rel_len / 2)] + ofs_rel[int(ofs_rel_len / 2) + 1]) / 2, 4)
                r['metrics']['overfilled_space_relative']['min'] = min(ofs_rel)
                r['metrics']['overfilled_space_relative']['max'] = max(ofs_rel)
            else:
                r['metrics']['overfilled_space_relative']['average'] = 0
                r['metrics']['overfilled_space_relative']['median'] = 0
                r['metrics']['overfilled_space_relative']['min'] = 0
                r['metrics']['overfilled_space_relative']['max'] = 0
        network_fs = []
        # noinspection PyTypeChecker
        n_ticks = len(list(reports_values)[0]['data_recorded']['filled_space'])
        n_nodes = len(reports_values)
        for i in range(n_ticks):
            val = 0
            for r in reports_values:
                val += r['data_recorded']['filled_space'][i]
            val /= n_nodes
            network_fs.append(val / network_capacity)



    def prepare_total(self):
        """
        Возвращает данные по показателям загрузки за все время у сети. Например, берется показатель усредненной
        загрузки сети в каждый тик. В отчете на выходе будут содержатся данные по среднему значению этой величины,
        медианному, минимальному и максимальному. То же самое по показателям медианной нагрузки на сеть, минимальной нагрузки на сеть,
        максимальной нагрузки на сеть, количеству переполненных узлов и суммарному объему памяти, на объем которой были
        превзойдены емкости каждого из узлов.
        Returns
        -------
        dict
        """
        average_filled_space_vals = []
        median_filled_space_vals = []
        min_filled_space_vals = []
        max_filled_space_vals = []
        overfilled_nodes_count_vals = []
        average_overfilled_space_vals = []
        median_overfilled_space_vals = []
        min_overfilled_space_vals = []
        max_overfilled_space_vals = []
        average_relative_overfilled_space_vals = []
        median_relative_overfilled_space_vals = []
        min_relative_overfilled_space_vals = []
        max_relative_overfilled_space_vals = []



        fs_matrix_T = [] # значения объединены по строкам (одна строка - один "тик" системы)
        # noinspection PyTypeChecker
        fs_len = len(self.__reports[list(self.__reports.keys())[0]]['data_recorded']['filled_space']) # исходим из предположения, что все длины одинаковые (иначе быть не может)
        for i in range(fs_len):
            fs_matrix_T.append([])
            for r in self.__reports.values():
                fs_matrix_T[i].append(r['data_recorded']['filled_space'][i])

        for line in fs_matrix_T:
            line_sum = sum(line)
            line_len = len(line)
            average_filled_space_vals.append(round(line_sum / line_len, 4))
            sorted_line = sorted(line)
            if line_len % 2 == 0:
                median_filled_space_vals.append(round(sorted_line[int(line_len / 2)], 4))
            else:
                median_filled_space_vals.append(round((sorted_line[int(line_len / 2)] + sorted_line[int(line_len / 2) + 1]) / 2, 4))
            min_filled_space_vals.append(min(line))
            max_filled_space_vals.append(max(line))


        ofs_matrix_T = []  # значения объединены по строкам (одна строка - один "тик" системы)
        ofs_len = len(self.__reports[list(self.__reports.keys())[0]]['data_recorded']['filled_space'])  # исходим из предположения, что все длины одинаковые (иначе быть не может)
        for i in range(ofs_len):
            ofs_matrix_T.append([])
            for r in self.__reports.values():
                capacity = r['capacity']
                fs = r['data_recorded']['filled_space'][i]
                ofs_matrix_T[i].append(fs - capacity if fs > capacity else 0)

        for line in ofs_matrix_T:
            overfilled_nodes_count_vals.append(sum([ofs > 0 for ofs in line]))
            line_sum = sum(line)
            line_len = len(line)
            average_overfilled_space_vals.append(round(line_sum / line_len, 4))
            sorted_line = sorted(line)
            if line_len % 2 == 0:
                median_overfilled_space_vals.append(round(sorted_line[int(line_len / 2)], 4))
            else:
                median_overfilled_space_vals.append(round((sorted_line[int(line_len / 2)] + sorted_line[int(line_len / 2) + 1]) / 2, 4))
            min_overfilled_space_vals.append(min(line))
            max_overfilled_space_vals.append(max(line))

        ofs_rel_matrix_T = []  # значения объединены по строкам (одна строка - один "тик" системы)
        ofs_rel_len = len(self.__reports[list(self.__reports.keys())[0]]['data_recorded']['filled_space'])  # исходим из предположения, что все длины одинаковые (иначе быть не может)
        for i in range(ofs_rel_len):
            ofs_rel_matrix_T.append([])
            for r in self.__reports.values():
                capacity = r['capacity']
                fs = r['data_recorded']['filled_space'][i]
                ofs_rel_matrix_T[i].append((fs - capacity) / capacity if fs > capacity else 0)

        for line in ofs_rel_matrix_T:
            line_sum = sum(line)
            line_len = len(line)
            average_relative_overfilled_space_vals.append(round(line_sum / line_len, 4))
            sorted_line = sorted(line)
            if line_len % 2 == 0:
                median_relative_overfilled_space_vals.append(round(sorted_line[int(line_len / 2)], 4))
            else:
                median_relative_overfilled_space_vals.append(round((sorted_line[int(line_len / 2)] + sorted_line[int(line_len / 2) + 1]) / 2, 4))
            min_relative_overfilled_space_vals.append(min(line))
            max_relative_overfilled_space_vals.append(max(line))





        for vals_list, vals_name in [
                          (average_filled_space_vals, 'average_filled_space'),
                          (median_filled_space_vals, 'median_filled_space'),
                          (min_filled_space_vals, 'min_filled_space'),
                          (max_filled_space_vals, 'max_filled_space'),
                          (overfilled_nodes_count_vals, 'overfilled_nodes_count'),
                          (average_overfilled_space_vals, 'average_overfilled_space'),
                          (median_overfilled_space_vals, 'median_overfilled_space'),
                          (min_overfilled_space_vals, 'min_overfilled_space'),
                          (max_overfilled_space_vals, 'max_overfilled_space'),
                          (average_relative_overfilled_space_vals, 'average_relative_overfilled_space'),
                          (median_relative_overfilled_space_vals, 'median_relative_overfilled_space'),
                          (min_relative_overfilled_space_vals, 'min_relative_overfilled_space'),
                          (max_relative_overfilled_space_vals, 'max_relative_overfilled_space')]:
            vals_sum = sum(vals_list)
            vals_len = len(vals_list)

            if vals_len != 0:
                self.__total[vals_name]['average'] = vals_sum / vals_len
                if vals_len % 2 == 0:
                    self.__total[vals_name]['median'] = round(vals_list[int(vals_len / 2)], 4)
                else:
                    self.__total[vals_name]['median'] = round((vals_list[int(vals_len / 2)] + vals_list[int(vals_len / 2) + 1]) / 2, 4)

                self.__total[vals_name]['min'] = min(vals_list)
                self.__total[vals_name]['max'] = max(vals_list)
            else:
                self.__total[vals_name]['average'] = 0
                self.__total[vals_name]['median'] = 0
                self.__total[vals_name]['min'] = 0
                self.__total[vals_name]['max'] = 0


    def prepare_general_info(self):
        max_node_r = None
        min_node_r = None
        max_node_avg = -1
        min_node_avg = 2

        overfilled_nodes_stats = {k: None for k in self.__reports.keys()}

        for node_r in self.__reports.values():
            if node_r['metrics']['filled_space_relative']['average'] > max_node_avg:
                max_node_r = node_r
                max_node_avg = node_r['metrics']['filled_space_relative']['average']
            elif node_r['metrics']['filled_space_relative']['average'] < min_node_avg:
                min_node_r = node_r
                min_node_avg = node_r['metrics']['filled_space_relative']['average']

            ticks_overfilled = 0
            for val in node_r['data_recorded']['filled_space']:
                if val > node_r['capacity']:
                    ticks_overfilled += 1

            ticks_overfilled /= len(node_r['data_recorded']['filled_space'])
            overfilled_nodes_stats[node_r['id']] = round(ticks_overfilled, 4)

        self.__general_info = {
            'max_filled_node': max_node_r,
            'min_filled_node': min_node_r,
            'overfilled_nodes_stats': overfilled_nodes_stats, # список
            'average_relative_filled_space': round(self.__total['average_filled_space']['average'] / self.__network.capacity, 6),
            'average_overfilled_nodes_relative_count': round(self.__total['overfilled_nodes_count']['average'] / len(self.__network), 4)
        }

    def save_to_excel(self):
        return NotImplemented

    def save_to_txt(self, file_path: str):
        with open(os.path.abspath(file_path), 'w', encoding='utf-8') as f:
            f.write('REPORTS:\n')
            s = json.dumps(self.__reports, indent=4, ensure_ascii=False)
            f.write(s)

            f.write('\n\n')

            f.write('TOTAL:\n')
            s = json.dumps(self.__total, indent=4, ensure_ascii=False)
            f.write(s)

            f.write('\n\n')

            f.write('GENERAL INFO:\n')
            s = json.dumps(self.__general_info, indent=4, ensure_ascii=False)
            f.write(s)



