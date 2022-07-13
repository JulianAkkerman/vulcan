import penman

from server.basic_layout import BasicLayout
from server.server import Server
from data_handling.data_corpus import from_dict_list
from am_parser.graph_dependency_parser.components.dataset_readers.amconll_tools import parse_amconll

if __name__ == "__main__":

    graphs = []
    amtrees = []
    sentences = []

    with open("../../../data/Edinburgh/amr3.0leamr_and_seq2seq/unanonymized/subset/full.amconll") as f:
        am_sentences = parse_amconll(f)

        for am_sentence in am_sentences:
            graph_string = am_sentence.attributes["original_graph_string"]
            graphs.append(graph_string)
            amtrees.append(str(am_sentence))
            sentences.append(" ".join([entry.token for entry in am_sentence.words]))


    input_dicts = [
        {
            "type": "data",
            "name": "graphs",
            "instances": graphs,
            "format": "graph_string"
        },
        {
            "type": "data",
            "name": "amtrees",
            "instances": amtrees,
            "format": "amtree_string"
        },
        {
            "type": "data",
            "name": "sentences",
            "instances": sentences,
            "format": "string"
        }
    ]

    data_corpus = from_dict_list(input_dicts)

    print(data_corpus.slices["amtrees"].instances[0])

    layout = BasicLayout(data_corpus.slices.values())

    print(layout.layout)

    server = Server(layout)
    server.start()  # at this point, the server is running on this thread, and nothing below will be executed




