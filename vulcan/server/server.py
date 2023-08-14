from typing import List, Dict, Set, Tuple, Any

import socketio
from eventlet import wsgi

from vulcan.data_handling.data_corpus import CorpusSlice
from vulcan.data_handling.linguistic_objects.graphs.penman_converter import from_penman_graph
import eventlet

from vulcan.data_handling.visualization_type import VisualizationType
from vulcan.server.basic_layout import BasicLayout

eventlet.monkey_patch()


def transform_string_maps_to_table_maps(highlights, label_alternatives_by_node_name):
    if label_alternatives_by_node_name:
        label_alternatives_by_node_name = {[0, k]: v for k, v in label_alternatives_by_node_name.items()}
    if highlights:
        highlights = {[0, k] for k in highlights}
    return highlights, label_alternatives_by_node_name


class Server:

    def __init__(self, layout: BasicLayout, port=5050, show_node_names=False):

        self.port = port
        self.current_layouts_by_sid = {}
        self.basic_layout = layout

        def on_connect(sid, environ):
            print(sid, 'connected')
            self.current_layouts_by_sid[sid] = self.basic_layout
            self.sio.emit('set_layout', make_layout_sendable(self.basic_layout))
            self.sio.emit('set_corpus_length', self.basic_layout.corpus_size)
            self.sio.emit('set_show_node_names', {"show_node_names": show_node_names})
            instance_requested(sid, 0)

        def on_disconnect(sid):
            print(sid, 'disconnected')
            self.current_layouts_by_sid.pop(sid)  # avoiding a memory leak

        self.sio = socketio.Server(async_mode='eventlet')
        self.sio.on("connect", on_connect)
        self.sio.on("disconnect", on_disconnect)
        self.app = socketio.WSGIApp(self.sio, static_files={
            '/': './vulcan/client/'
        })

        @self.sio.event
        def instance_requested(sid, data):
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

        @self.sio.event
        def perform_search(sid, data):
            corpus_slice_name: str = data["corpus_slice_name"]
            outer_search_layer_name: str = data["outer_search_layer_name"]
            inner_search_layer_names: List[str] = data["inner_search_layer_names"]
            inner_search_layer_arguments: List[List[str]] = data["inner_search_layer_arguments"]
            self.current_layouts_by_sid[sid] = self.basic_layout.perform_search(corpus_slice_name,
                                                                                outer_search_layer_name,
                                                                                inner_search_layer_names,
                                                                                inner_search_layer_arguments)
            self.sio.emit('set_corpus_length', self.current_layouts_by_sid[sid].corpus_size)
            self.sio.emit('search_completed', None)

    def start(self):
        wsgi.server(eventlet.listen(('localhost', self.port)), self.app)

    def send_string(self, slice_name: str, tokens: List[str], label_alternatives_by_node_name: Dict = None,
                    highlights: Set[int] = None,
                    dependency_tree: List[Tuple[int, int, str]] = None):
        highlights, label_alternatives_by_node_name = transform_string_maps_to_table_maps(highlights,
                                                                                          label_alternatives_by_node_name)
        self.send_string_table(slice_name, [[t] for t in tokens], label_alternatives_by_node_name, highlights, dependency_tree)

    def send_string_table(self, slice_name: str, table: List[List[str]],
                          label_alternatives_by_node_name: Dict[Tuple[int, int], Any] = None,
                          highlights: Set[Tuple[int, int]] = None,
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
                   highlights: Set[str] = None, mouseover_texts: Dict[str, str] = None):
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
        self.sio.emit('set_linker', {"name1": name1, "name2": name2, "scores": scores})


def make_layout_sendable(layout: BasicLayout):
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
