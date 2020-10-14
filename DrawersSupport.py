from dataclasses import dataclass
from types import MappingProxyType

from Paths import PathCollection


@dataclass
class BaseDrawerConfig():
    dpi: int = 100
    standard_nodes_color: str = '#949494'
    inc_nodes_color: str = '#5dff4f'
    dec_nodes_color: str = '#fc2a2a'

    font_family: str = 'sans-serif'
    font_weight: str = 'bold'
    font_color: str = 'black'

    edge_style = 'solid'
    edge_neutral_color: str = 'black'
    edge_neutral_width: int = 4.5
    edge_label_bbox: MappingProxyType = MappingProxyType({
        'facecolor': '#ffffff',
        'edgecolor': '#ffffff',
        'alpha': 0.6,
        'pad': 0}) # immutable dict

    arrowstyle = '-|>' # ->, fancy, simple, wedge, -|>
    arrowsize = 40
    arrows = True
    connectionstyle = None
    min_source_marg = -2
    min_target_marg = 0

    weights_label_pos: float = 0.4  # или (0.5 * random.ranf() + 0.25)
    weights_font_size: int = 15

    node_shape: str = 's'
    node_size: int = 850
    node_font_size: int = 18
    node_neutral_color: str = '#949494'
    node_borders_width: float = 1.5
    node_borders_color: str = 'k'
    # node_label_bbox: MappingProxyType = MappingProxyType({}) # immutable dict
    node_label_bbox = None
    node_label_horizontalalignment: str = "center"
    node_label_verticalalignment: str = "center"
    # font_size = 16

    first_path_hex_color: str = '0x08e822'
    path_edges_width: float = 6

############
# PARAMS
############

class TextBoxParams:
    def __init__(self,
                 graph_info: dict,
                 paths: PathCollection
                 ):

        self._graph_info = graph_info
        self._graph_type = self._graph_info.get('graph_type')
        self._paths = paths

        self.x = -0.14
        self.y = 0.03 + 0.012 * len(self._paths)
        self.fontstyle = 'normal'
        self.fontsize = 15


        self.vertical_alignment = 'top'
        self.horizontal_alignment = 'left'

        self.bbox = {
            'facecolor': '#89ebf1',
            'alpha': 0.7,
            'pad': 5}

    @property
    def digraph_info(self):
        paths_string = '{'
        L = len(self._paths) if len(self._paths) <= 10 else 10

        for i in range(0, L):
            if i != L - 1:
                paths_string += str(self._paths[i]) + ', ' + '\n' * (i % 2)
            else:
                paths_string += str(self._paths[i]) + '}'

        if self._graph_type == 'standard':
            digraph_info = f'Paths: {paths_string}\nReachability type: Standard'
        elif self._graph_type == 'vmrk':
            k_min = self._graph_info.get('k_min')
            digraph_info = f'Paths: {paths_string}\nReachability type: VMR of k degree\nk_min = {k_min}'
        elif self._graph_type == 'mnrk':
            digraph_info = ...
        elif self._graph_type == 'telnet':
            digraph_info = ...
        elif self._graph_type == 'vmrk_telnet':
            digraph_info = ...
        elif self._graph_type == 'mnrk_telnet':
            digraph_info = ...
        else:
            raise ValueError(f'Graph type "{self._graph_type}" not recognized')

        return digraph_info