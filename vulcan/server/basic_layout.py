from data_handling.data_corpus import CorpusSlice
from data_handling.visualization_type import VisualizationType


class BasicLayout:

    def __init__(self, slices, linkers, corpus_size, message):
        self.layout = []
        last_active_row = []
        self.layout.append(last_active_row)
        for slice in slices:
            if get_slice_screen_width(slice) >= 1.0:
                self.layout.append([slice])
                continue
            current_fill = sum([get_slice_screen_width(s) for s in last_active_row])
            if current_fill + get_slice_screen_width(slice) > 1:
                last_active_row = [slice]
                self.layout.append(last_active_row)
            else:
                last_active_row.append(slice)
        if [] in self.layout:
            self.layout.remove([])  # if last_active_row is still empty, we remove it
        self.linkers = linkers
        self.corpus_size = corpus_size
        self.message = message


def get_slice_screen_width(corpus_slice: CorpusSlice) -> float:
    if corpus_slice.visualization_type == VisualizationType.STRING:
        return 1.0
    elif corpus_slice.visualization_type in [VisualizationType.TREE, VisualizationType.GRAPH]:
        return 0.3
