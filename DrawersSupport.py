class PlaneGraphParams:
    def __init__(self, nodes_count: int):

        self.figure_size = (int(13 * nodes_count / 11), int(7 * nodes_count / 11))
        self.node_size = 450
        self.node_font_size = 16

class TextBoxParams:
    def __init__(self,
                 graph_info: dict,
                 paths: list):

        self._graph_info = graph_info
        self._graph_type = self._graph_info.get('type')
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
                paths_string += str(self._paths[i]) + '\n}'

        if self._graph_type == 'standard':
            digraph_info = (f'Paths: {paths_string}\nReachability type: Standard')
        elif self._graph_type == 'vmrk':
            k = self._graph_info.get('k')
            digraph_info = (f'Paths: {paths_string}\nReachability type: VMR of k degree\nk = {k}')
        elif ...:
            ...
        elif ...:
            ...
        elif ...:
            ...
        elif ...:
            ...

        return digraph_info