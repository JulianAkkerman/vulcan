import json
import pickle

from vulcan.file_loader import create_layout_from_filepath
from vulcan.data_handling.data_corpus import from_dict_list
from vulcan.server.basic_layout import BasicLayout
from vulcan.server.server import Server, make_layout_sendable


def launch_server_from_file(input_path: str, port: int = 5050, address: str = "localhost", is_json_file: bool = False,
                            show_node_names: bool = False, propbank_path: str = None,
                            show_wikipedia_articles: bool = False):

    layout = create_layout_from_filepath(input_path, is_json_file, propbank_path, show_wikipedia_articles)

    server = Server(layout, port=port, address=address, show_node_names=show_node_names)

    server.start()  # at this point, the server is running on this thread, and nothing below will be executed



