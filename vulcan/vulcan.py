import pickle

import penman

from data_handling.linguistic_objects.trees.am_tree_as_dict import generate_random_label_alternatives, \
    alignments_from_amtree
from server.basic_layout import BasicLayout
from server.server import Server
from data_handling.data_corpus import from_dict_list
from am_parser.graph_dependency_parser.components.dataset_readers.amconll_tools import parse_amconll


def main():
    with open("../../am-text-generation/models/analysis/base/vulcan_490.pickle", "rb") as f:
        input_dicts = pickle.load(f)

    data_corpus = from_dict_list(input_dicts)

    layout = BasicLayout(data_corpus.slices.values(), data_corpus.linkers)

    print(layout.layout)

    server = Server(layout)
    server.start()  # at this point, the server is running on this thread, and nothing below will be executed


def make_graph_amtree_example():
    graphs = []
    amtrees = []
    sentences = []
    with open("../../../data/Edinburgh/amr3.0leamr_and_seq2seq/unanonymized/subset/full.amconll") as f:
        am_sentences = parse_amconll(f)

        for am_sentence in am_sentences:
            graph_string = am_sentence.attributes["original_graph_string"]
            graphs.append(graph_string)
            amtrees.append(am_sentence)
            sentences.append([entry.token for entry in am_sentence.words])
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
            "format": "amtree",
            "label_alternatives": [generate_random_label_alternatives(amtree) for amtree in amtrees]
        },
        {
            "type": "data",
            "name": "sentences",
            "instances": sentences,
            "format": "tokenized_string"
        },
        {
            "type": "linker",
            "name1": "amtrees",
            "name2": "sentences",
            "scores": [alignments_from_amtree(amtree) for amtree in amtrees]
        }
    ]

    return input_dicts


if __name__ == '__main__':
    main()
