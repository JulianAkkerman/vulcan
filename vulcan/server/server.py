import socketio
from eventlet import wsgi
from data_handling.linguistic_objects.graphs.penman_converter import from_penman_graph
import eventlet
eventlet.monkey_patch()


class Server:

    def __init__(self, graphs, port=5050):

        self.current_position = [0]
        self.graphs = graphs

        def on_connect(sid, environ):
            print(sid, 'connected')
            sio.emit("make_graph", from_penman_graph(self.graphs[self.current_position[0]]))
            sio.emit("set_corpus_position", {"current": self.current_position[0], "total": len(self.graphs)})

        def on_disconnect(sid):
            print(sid, 'disconnected')

        sio = socketio.Server(async_mode='eventlet')
        sio.on("connect", on_connect)
        sio.on("disconnect", on_disconnect)
        self.app = socketio.WSGIApp(sio, static_files={
            '/': './client/'
        })

        @sio.event
        def next_button_clicked(sid):
            if self.current_position[0] < len(self.graphs)-1:
                self.current_position[0] += 1
            sio.emit("make_graph", from_penman_graph(self.graphs[self.current_position[0]]))
            sio.emit("set_corpus_position", {"current": self.current_position[0], "total": len(self.graphs)})

        @sio.event
        def previous_button_clicked(sid):
            if self.current_position[0] > 0:
                self.current_position[0] -= 1
            sio.emit("make_graph", from_penman_graph(self.graphs[self.current_position[0]]))
            sio.emit("set_corpus_position", {"current": self.current_position[0], "total": len(self.graphs)})

    def start(self):
        wsgi.server(eventlet.listen(('localhost', 5050)), self.app)

    def set_graphs(self, graphs):
        self.graphs = graphs
