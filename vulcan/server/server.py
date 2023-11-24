from typing import List, Dict, Set, Tuple, Any, Union

import socketio
from eventlet import wsgi

import vulcan.search
from vulcan.search.search import SearchFilter, perform_search_on_layout, create_list_of_possible_search_filters
from vulcan.data_handling.data_corpus import CorpusSlice
from vulcan.data_handling.linguistic_objects.graphs.penman_converter import from_penman_graph
from vulcan.data_handling.linguistic_objects.table import cell_coordinates_to_cell_name
import eventlet

from vulcan.data_handling.visualization_type import VisualizationType
from vulcan.server.basic_layout import BasicLayout
import logging

eventlet.monkey_patch()

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def transform_string_maps_to_table_maps(highlights: Dict[int, Union[str, List[str]]],
                                        label_alternatives_by_node_name: Dict[int, Dict[str, Any]]):
    if label_alternatives_by_node_name:
        label_alternatives_by_node_name = {cell_coordinates_to_cell_name(0, k): v for k, v in label_alternatives_by_node_name.items()}
    if highlights:
        highlights = {cell_coordinates_to_cell_name(0, k): v for k, v in highlights.items()}
    return highlights, label_alternatives_by_node_name


class Server:

    def __init__(self, create_layout_function, port=5050, show_node_names=False):

        self.port = port
        self.current_layouts_by_sid = {}

        def on_connect(sid, environ):
            try:
                print(sid, 'connected')
                # self.current_layouts_by_sid[sid] = self.basic_layout
                # self.sio.emit('set_layout', make_layout_sendable(self.basic_layout))
                # self.sio.emit('set_corpus_length', self.basic_layout.corpus_size)
                self.sio.emit('set_show_node_names', {"show_node_names": show_node_names})
                # # print("sending search filters", create_list_of_possible_search_filters(self.basic_layout))
                # self.sio.emit('set_search_filters', create_list_of_possible_search_filters(self.basic_layout))
                # instance_requested(sid, 0)
            except Exception as e:
                logger.exception(e)
                self.sio.emit("server_error")

        def on_disconnect(sid):
            print(sid, 'disconnected')

        self.sio = socketio.Server(async_mode='eventlet')
        self.sio.on("connect", on_connect)
        self.sio.on("disconnect", on_disconnect)
        self.app = socketio.WSGIApp(self.sio, static_files={
            '/': './vulcan/client/'
        })

        @self.sio.event
        def instance_requested(sid, data):
            try:
                if self.current_layouts_by_sid[sid].corpus_size > 0:
                    instance_id = data
                    for row in self.current_layouts_by_sid[sid].layout:
                        for corpus_slice in row:
                            if corpus_slice.label_alternatives is not None:
                                label_alternatives_by_node_name = corpus_slice.label_alternatives[instance_id]
                            else:
                                label_alternatives_by_node_name = None
                            if corpus_slice.highlights is not None:
                                highlights = corpus_slice.highlights[instance_id]
                            else:
                                highlights = None
                            if corpus_slice.mouseover_texts is not None:
                                mouseover_texts = corpus_slice.mouseover_texts[instance_id]
                            else:
                                mouseover_texts = None
                            if corpus_slice.dependency_trees is not None:
                                dependency_tree = corpus_slice.dependency_trees[instance_id]
                            else:
                                dependency_tree = None
                            if corpus_slice.visualization_type == VisualizationType.STRING:
                                self.send_string(corpus_slice.name,
                                                 corpus_slice.instances[instance_id],
                                                 label_alternatives_by_node_name,
                                                 highlights,
                                                 dependency_tree)
                            elif corpus_slice.visualization_type == VisualizationType.TABLE:
                                self.send_string_table(corpus_slice.name,
                                                       corpus_slice.instances[instance_id],
                                                       label_alternatives_by_node_name,
                                                       highlights,
                                                       dependency_tree)
                            elif corpus_slice.visualization_type == VisualizationType.TREE:
                                # trees are just graphs without reentrancies
                                self.send_graph(corpus_slice.name, corpus_slice.instances[instance_id],
                                                label_alternatives_by_node_name,
                                                highlights)
                            elif corpus_slice.visualization_type == VisualizationType.GRAPH:
                                self.send_graph(corpus_slice.name, corpus_slice.instances[instance_id],
                                                label_alternatives_by_node_name,
                                                highlights, mouseover_texts)
                    for linker in self.current_layouts_by_sid[sid].linkers:
                        self.send_linker(linker["name1"], linker["name2"], linker["scores"][instance_id])
                else:
                    print("No instances in corpus")
            except Exception as e:
                logger.exception(e)
                self.sio.emit("server_error")

        @self.sio.event
        def parse(sid, data):
            self.current_layouts_by_sid[sid] = create_layout_function(data)
            self.sio.emit('set_layout', make_layout_sendable(self.current_layouts_by_sid[sid]))

    def start(self):
        wsgi.server(eventlet.listen(('localhost', self.port)), self.app)

    def send_string(self, slice_name: str, tokens: List[str], label_alternatives_by_node_name: Dict = None,
                    highlights: Dict[int, Union[str, List[str]]] = None,
                    dependency_tree: List[Tuple[int, int, str]] = None):
        highlights,\
        label_alternatives_by_node_name = transform_string_maps_to_table_maps(highlights,
                                                                              label_alternatives_by_node_name)
        self.send_string_table(slice_name, [[t] for t in tokens], label_alternatives_by_node_name, highlights,
                               dependency_tree)

    def send_string_table(self, slice_name: str, table: List[List[str]],
                          label_alternatives_by_node_name: Dict[Tuple[int, int], Any] = None,
                          highlights: Dict[Tuple[int, int], Union[str, List[str]]] = None,
                          dependency_tree: List[Tuple[int, int, str]] = None):
        dict_to_sent = {"canvas_name": slice_name, "table": table}
        if label_alternatives_by_node_name is not None:
            dict_to_sent["label_alternatives_by_node_name"] = label_alternatives_by_node_name
        if highlights is not None:
            dict_to_sent["highlights"] = highlights
        if dependency_tree is not None:
            dict_to_sent["dependency_tree"] = dependency_tree
        self.sio.emit('set_table', dict_to_sent)

    def send_graph(self, slice_name: str, graph: Dict, label_alternatives_by_node_name: Dict = None,
                   highlights: Dict[str, Union[str, List[str]]] = None, mouseover_texts: Dict[str, str] = None):
        """
        graph must be of the graph_as_dict type.
        """
        dict_to_sent = {"canvas_name": slice_name, "graph": graph}
        if label_alternatives_by_node_name is not None:
            dict_to_sent["label_alternatives_by_node_name"] = label_alternatives_by_node_name
        if highlights is not None:
            dict_to_sent["highlights"] = highlights
        if mouseover_texts is not None:
            dict_to_sent["mouseover_texts"] = mouseover_texts
        self.sio.emit('set_graph', dict_to_sent)

    def send_linker(self, name1: str, name2: str, scores: Dict[str, Dict[str, float]]):
        if self.basic_layout.get_visualization_type_for_slice_name(name1) == VisualizationType.STRING:
            scores = {str((0, k)).replace("'", ""): v for k, v in scores.items()}
        if self.basic_layout.get_visualization_type_for_slice_name(name2) == VisualizationType.STRING:
            scores = {k: {str((0, k2)).replace("'", ""): v for k2, v in d.items()} for k, d in scores.items()}
        self.sio.emit('set_linker', {"name1": name1, "name2": name2, "scores": scores})


def make_layout_sendable(layout: BasicLayout):
    print("make_layout_sendable", layout)
    ret = []
    for row in layout.layout:
        ret.append([make_slice_sendable(s) for s in row])
    return ret


def make_slice_sendable(corpus_slice: CorpusSlice):
    ret = {
        "name": corpus_slice.name,
        "visualization_type": corpus_slice.visualization_type,
    }
    return ret


def get_search_filters_from_data(data):
    search_filters = []
    for search_filter_data in data:
        search_filters.append(SearchFilter(search_filter_data["slice_name"], search_filter_data["outer_layer_id"],
                                           search_filter_data["inner_layer_ids"],
                                           search_filter_data["inner_layer_inputs"],
                                           search_filter_data["color"]))
    return search_filters
