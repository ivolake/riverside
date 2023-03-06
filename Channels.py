import math
from collections import OrderedDict
import additions as adds

from Packets import BasePacket


class BaseChannel:
    def __init__(self,
                 channel_id: str,
                 source,
                 target,
                 processing_speed: float | None,
                 **kwargs):
        self.id = channel_id
        self.source = source
        self.target = target
        self._processing_speed = processing_speed

        self._records = OrderedDict({})  # еще не отправленные содержащиеся на узле пакеты (хранение в виде {pkt.id: pkt})

    def __repr__(self):
        return adds.Representation(self, ['id', 'source_id', 'target_id', 'filled_space', '_records_len'])()

    @property
    def records(self):  # -> OrderedDict[str, BasePacket]:
        return self._records

    @property
    def source_id(self):  # -> OrderedDict[str, BasePacket]:
        return self.source.id if self.source is not None else None

    @property
    def target_id(self):  # -> OrderedDict[str, BasePacket]:
        return self.target.id if self.target is not None else None

    @property
    def filled_space(self):
        records = self.records.values()
        if len(records) == 0:
            records_sum = 0
        else:
            records_sum = sum([record['packet'].size for record in records])
        return records_sum

    @property
    def _records_len(self):
        return len(self.records)


    def add_to_records(self,
                       pkt: BasePacket,
                       departure_time: float):
        if pkt is not None:
            self._records.update({
                f'{pkt.sid}.{pkt.pid}.{pkt.id}': {
                    'packet': pkt,
                    'departure_time': departure_time,
                }
            })
        else:
            return -1

    def pop_from_records(self, pkt: BasePacket):
        if pkt is not None:
            return self._records.pop(f'{pkt.sid}.{pkt.pid}.{pkt.id}')
        else:
            return -1

    def get_packet_travel_time(self, pkt: BasePacket):
        return pkt.size / self._processing_speed

    def flush(self):
        """
        Очистить очереди
        Returns
        -------

        """
        self._records = OrderedDict({})
