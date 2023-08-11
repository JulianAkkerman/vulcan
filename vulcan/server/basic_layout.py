from typing import List, Any, Optional

from search.inner_search_layer import InnerSearchLayer
from search.outer_search_layer import OuterSearchLayer
from search.table_cells.cell_content_equals import CellContentEquals
from search.table_cells.outer_table_cells_layer import OuterTableCellsLayer
from vulcan.data_handling.data_corpus import CorpusSlice
from vulcan.data_handling.visualization_type import VisualizationType


# TODO these lists should probably be in their own files. Maybe also this should be structured differently. Let's
#  see how working with this goes.
OUTER_SEARCH_LAYERS = {
    "OuterTableCellsLayer": OuterTableCellsLayer()
}

INNER_SEARCH_LAYERS = {
    "CellContentEquals": CellContentEquals()
}




class BasicLayout:

    def __init__(self, slices, linkers, corpus_size):
        self.layout: List[List[CorpusSlice]] = []
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

    def perform_search(self,
                       corpus_slice_name: str,
                       outer_search_layer_name: str,
                       inner_search_layer_names: List[str],
                       inner_search_layer_arguments: List[List[str]]) -> 'BasicLayout':
        list_to_search: List[any] = self.get_list_to_search(corpus_slice_name)
        matching_indices = search_list(list_to_search, outer_search_layer_name, inner_search_layer_names,
                                            inner_search_layer_arguments)
        slices = self.get_sub_slices_from_indices(matching_indices)
        linkers = self.get_sub_linkers_from_indices(matching_indices)
        return BasicLayout(slices, linkers, len(matching_indices))

    def get_list_to_search(self, corpus_slice_name: str) -> List[any]:
        for row in self.layout:
            for corpus_slice in row:
                if corpus_slice.name == corpus_slice_name:
                    return corpus_slice.instances
        for linker_index, linker in enumerate(self.linkers):
            if get_linker_name(linker, linker_index) == corpus_slice_name:
                return linker["scores"]
        raise Exception("Corpus slice not found: " + corpus_slice_name)

    def get_sub_slices_from_indices(self, matching_indices: List[int]) -> List[CorpusSlice]:
        sub_slices = []
        for row in self.layout:
            for corpus_slice in row:
                new_instances = filter_part_of_slice(corpus_slice.instances, matching_indices)
                new_label_alternatives = filter_part_of_slice(corpus_slice.label_alternatives, matching_indices)
                new_highlights = filter_part_of_slice(corpus_slice.highlights, matching_indices)
                new_mouseover_texts = filter_part_of_slice(corpus_slice.mouseover_texts, matching_indices)
                new_dependency_trees = filter_part_of_slice(corpus_slice.dependency_trees, matching_indices)

                new_slice = CorpusSlice(corpus_slice.name, new_instances,
                                        corpus_slice.visualization_type,
                                        label_alternatives=new_label_alternatives,
                                        highlights=new_highlights,
                                        mouseover_texts=new_mouseover_texts,
                                        dependency_trees=new_dependency_trees)
                sub_slices.append(new_slice)
        return sub_slices

    def get_sub_linkers_from_indices(self, matching_indices: List[int]) -> List[dict]:
        sub_linkers = []
        for linker_index, linker in enumerate(self.linkers):
            new_scores = filter_part_of_slice(linker["scores"], matching_indices)
            new_linker = {"name1": linker["name1"],
                          "name2": linker["name2"],
                          "scores": new_scores}
            sub_linkers.append(new_linker)
        return sub_linkers


def filter_part_of_slice(part_of_slice: Optional[List[Any]], matching_indices: List[int]) -> Optional[List[Any]]:
    if part_of_slice is not None:
        return [part_of_slice[i] for i in matching_indices]
    else:
        return None


def get_linker_name(linker, linker_index):
    return f"linker{linker_index} {linker['name1']} - {linker['name2']}"


def get_slice_screen_width(corpus_slice: CorpusSlice) -> float:
    if corpus_slice.visualization_type in [VisualizationType.STRING, VisualizationType.TABLE]:
        return 1.0
    elif corpus_slice.visualization_type in [VisualizationType.TREE, VisualizationType.GRAPH]:
        return 0.3


def search_list(list_to_search: List[any],
                outer_search_layer_name: str,
                inner_search_layer_names: List[str],
                inner_search_layer_arguments: List[List[str]]) -> List[int]:
    outer_search_layer: OuterSearchLayer = get_outer_search_layer(outer_search_layer_name)
    inner_search_layers: List[InnerSearchLayer] = [get_inner_search_layer(name) for name in inner_search_layer_names]
    ret = []
    for index, item in enumerate(list_to_search):
        if outer_search_layer.apply(inner_search_layers, inner_search_layer_arguments, item):
            ret.append(index)
    return ret


def get_outer_search_layer(name: str) -> OuterSearchLayer:
    return OUTER_SEARCH_LAYERS[name]


def get_inner_search_layer(name: str) -> InnerSearchLayer:
    return INNER_SEARCH_LAYERS[name]
