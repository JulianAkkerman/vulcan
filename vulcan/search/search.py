from typing import List, Optional, Any

from data_handling.data_corpus import CorpusSlice
from search.graph_nodes.node_content_equals import NodeContentEquals
from search.graph_nodes.outer_graph_node_layer import OuterGraphNodeLayer
from search.inner_search_layer import InnerSearchLayer
from search.outer_search_layer import OuterSearchLayer
from search.search_registry import OUTER_SEARCH_LAYERS, INNER_SEARCH_LAYERS, VISUALIZATION_TYPE_TO_OUTER_SEARCH_LAYERS, \
    OUTER_TO_INNER_SEARCH_LAYERS
from search.table.column_count_at_least import ColumnCountAtLeast
from search.table.outer_table_as_a_whole_layer import OuterTableAsAWholeLayer
from search.table_cells.cell_content_equals import CellContentEquals
from search.table_cells.cell_content_matches import CellContentMatches
from search.table_cells.outer_table_cells_layer import OuterTableCellsLayer
from server.basic_layout import BasicLayout




class SearchFilter:
    def __init__(self, corpus_slice_name: str,
                 outer_search_layer_name: str, inner_search_layer_names: List[str],
                 inner_search_layer_arguments: List[List[str]]):
        self.corpus_slice_name = corpus_slice_name
        self.outer_search_layer_name = outer_search_layer_name
        self.inner_search_layer_names = inner_search_layer_names
        self.inner_search_layer_arguments = inner_search_layer_arguments


def perform_search_on_layout(layout: BasicLayout,
                             filters: List[SearchFilter]) -> 'BasicLayout':
    lists_to_search: List[List[any]] = [_get_list_to_search(layout, f.corpus_slice_name) for f in filters]
    matching_indices = _search_lists(lists_to_search, filters)
    slices = _get_sub_slices_from_indices(layout, matching_indices)
    linkers = _get_sub_linkers_from_indices(layout, matching_indices)
    return BasicLayout(slices, linkers, len(matching_indices))


def _get_list_to_search(layout: BasicLayout, corpus_slice_name: str) -> List[any]:
    for row in layout.layout:
        for corpus_slice in row:
            if corpus_slice.name == corpus_slice_name:
                return corpus_slice.instances
    for linker_index, linker in enumerate(layout.linkers):
        if _get_linker_name(linker, linker_index) == corpus_slice_name:
            return linker["scores"]
    raise Exception("Corpus slice not found: " + corpus_slice_name)


def _get_sub_slices_from_indices(layout: BasicLayout, matching_indices: List[int]) -> List[CorpusSlice]:
    sub_slices = []
    for row in layout.layout:
        for corpus_slice in row:
            new_instances = _filter_part_of_slice(corpus_slice.instances, matching_indices)
            new_label_alternatives = _filter_part_of_slice(corpus_slice.label_alternatives, matching_indices)
            new_highlights = _filter_part_of_slice(corpus_slice.highlights, matching_indices)
            new_mouseover_texts = _filter_part_of_slice(corpus_slice.mouseover_texts, matching_indices)
            new_dependency_trees = _filter_part_of_slice(corpus_slice.dependency_trees, matching_indices)

            new_slice = CorpusSlice(corpus_slice.name, new_instances,
                                    corpus_slice.visualization_type,
                                    label_alternatives=new_label_alternatives,
                                    highlights=new_highlights,
                                    mouseover_texts=new_mouseover_texts,
                                    dependency_trees=new_dependency_trees)
            sub_slices.append(new_slice)
    return sub_slices


def _get_sub_linkers_from_indices(layout: BasicLayout, matching_indices: List[int]) -> List[dict]:
    sub_linkers = []
    for linker_index, linker in enumerate(layout.linkers):
        new_scores = _filter_part_of_slice(linker["scores"], matching_indices)
        new_linker = {"name1": linker["name1"],
                      "name2": linker["name2"],
                      "scores": new_scores}
        sub_linkers.append(new_linker)
    return sub_linkers


def _filter_part_of_slice(part_of_slice: Optional[List[Any]], matching_indices: List[int]) -> Optional[List[Any]]:
    if part_of_slice is not None:
        return [part_of_slice[i] for i in matching_indices]
    else:
        return None


def _get_linker_name(linker, linker_index):
    return f"linker{linker_index} {linker['name1']} - {linker['name2']}"


def _search_lists(lists_to_search: List[List[any]],
                  filters: List[SearchFilter]) -> List[int]:
    outer_search_layers: List[OuterSearchLayer] = [get_outer_search_layer(f.outer_search_layer_name) for f in filters]
    inner_search_layers_list: List[List[InnerSearchLayer]] = [[get_inner_search_layer(name)
                                                          for name in f.inner_search_layer_names]
                                                            for f in filters]
    matching_indices = []
    node_names_for_highlighting = []
    for index, items in enumerate(zip(*lists_to_search)):
        success = True
        highlighting_here = {}
        for outer_search_layer, inner_search_layers, inner_search_layer_arguments, item in \
                zip(outer_search_layers, inner_search_layers_list, [f.inner_search_layer_arguments for f in filters], items):
            node_names_here = outer_search_layer.apply(inner_search_layers, inner_search_layer_arguments, item)
            if node_names_here is None:
                # print(f"Search returned false for: {outer_search_layer.get_label()},"
                #       f" {[l.get_label() for l in inner_search_layers]}, {inner_search_layer_arguments}, {item}")
                success = False
                break
        if success:
            matching_indices.append(index)
    return matching_indices


def get_outer_search_layer(name: str) -> OuterSearchLayer:
    return OUTER_SEARCH_LAYERS[name]


def get_inner_search_layer(name: str) -> InnerSearchLayer:
    return INNER_SEARCH_LAYERS[name]


def create_list_of_possible_search_filters(layout: BasicLayout):
    ret = {}
    for row in layout.layout:
        for corpus_slice in row:
            name = corpus_slice.name
            visualization_type = corpus_slice.visualization_type
            slice_dict = {}
            for outer_search_layer_id in VISUALIZATION_TYPE_TO_OUTER_SEARCH_LAYERS[visualization_type]:
                outer_search_layer = OUTER_SEARCH_LAYERS[outer_search_layer_id]
                outer_layer_dict = {"label": outer_search_layer.get_label(),
                                    "description": outer_search_layer.get_description(),
                                    "innerLayers": {}}
                for inner_search_layer_id in OUTER_TO_INNER_SEARCH_LAYERS[outer_search_layer_id]:
                    inner_search_layer = INNER_SEARCH_LAYERS[inner_search_layer_id]
                    inner_layer_dict = {"label": inner_search_layer.get_label(),
                                        "description": inner_search_layer.get_description()}
                    outer_layer_dict["innerLayers"][inner_search_layer_id] = inner_layer_dict

                slice_dict[outer_search_layer_id] = outer_layer_dict

            ret[name] = slice_dict
    return ret

