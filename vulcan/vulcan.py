import pickle
import sys

from data_handling.judgement_writer import JudgementWriter
from data_handling.linguistic_objects.trees.am_tree_as_dict import generate_random_label_alternatives, \
    alignments_from_amtree
from server.basic_layout import BasicLayout
from server.server import Server
from data_handling.data_corpus import from_dict
from amconll import parse_amconll


def main(args):
    # with open("../../amr-challenge/amrbank-analysis/outputs/negations_testset.pkl", "rb") as f:
    # "../../../data/vulcan_25.pickle"
    pickle_path = args[1]
    with open(pickle_path, "rb") as f:
        input_dicts = pickle.load(f)

    # input_dicts = make_highlights_example()

    data_corpus = from_dict(input_dicts)
    judgement_writer = JudgementWriter(pickle_path)
    judgement_writer.load_from_file_if_exists_else_init_rows(data_corpus)

    layout = BasicLayout(data_corpus.slices.values(), data_corpus.linkers, data_corpus.size, data_corpus.message)

    print(layout.layout)

    server = Server(layout, judgement_writer)
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


def make_highlights_example():
    graphs = ["(a / a :ARG0 (b / b))"]
    strings = [["a", "b"]]

    input_dicts = [
        {
            "type": "data",
            "name": "graphs",
            "instances": graphs,
            "format": "graph_string",
            "highlights": [["a"]]
        },
        {
            "type": "data",
            "name": "strings",
            "instances": strings,
            "format": "tokenized_string",
            "highlights": [[1]]
        },
    ]

    return input_dicts


if __name__ == '__main__':
    main(sys.argv)
