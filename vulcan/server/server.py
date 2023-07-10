from typing import List, Dict, Set

import socketio
from eventlet import wsgi

from vulcan.data_handling.data_corpus import CorpusSlice
from vulcan.data_handling.linguistic_objects.graphs.penman_converter import from_penman_graph
import eventlet

from vulcan.data_handling.visualization_type import VisualizationType
from vulcan.server.basic_layout import BasicLayout

eventlet.monkey_patch()


class Server:

    def __init__(self, layout: BasicLayout, port=5050, show_node_names=False):

        self.port = port

        def on_connect(sid, environ):
            print(sid, 'connected')
            self.sio.emit('set_layout', make_layout_sendable(layout))
            self.sio.emit('set_corpus_length', layout.corpus_size)
            self.sio.emit('set_show_node_names', {"show_node_names": show_node_names})
            instance_requested(sid, 0)

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
            instance_id = data
            for row in layout.layout:
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
                    if corpus_slice.visualization_type == VisualizationType.STRING:
                        self.send_string(corpus_slice.name,
                                         corpus_slice.instances[instance_id],
                                         label_alternatives_by_node_name,
                                         highlights)
                    elif corpus_slice.visualization_type == VisualizationType.TREE:
                        # trees are just graphs without reentrancies
                        self.send_graph(corpus_slice.name, corpus_slice.instances[instance_id],
                                        label_alternatives_by_node_name,
                                        highlights)
                    elif corpus_slice.visualization_type == VisualizationType.GRAPH:
                        self.send_graph(corpus_slice.name, corpus_slice.instances[instance_id],
                                        label_alternatives_by_node_name,
                                        highlights, mouseover_texts)
            for linker in layout.linkers:
                self.send_linker(linker["name1"], linker["name2"], linker["scores"][instance_id])

    def start(self):
        wsgi.server(eventlet.listen(('localhost', self.port)), self.app)

    def send_string(self, slice_name: str, tokens: List[str], label_alternatives_by_node_name: Dict = None,
                    highlights: Set[int] = None):
        dict_to_sent = {"canvas_name": slice_name, "tokens": tokens}
        if label_alternatives_by_node_name is not None:
            dict_to_sent["label_alternatives_by_node_name"] = label_alternatives_by_node_name
        if highlights is not None:
            dict_to_sent["highlights"] = highlights
        self.sio.emit('set_string', dict_to_sent)

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


