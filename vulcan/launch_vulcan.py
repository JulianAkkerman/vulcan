import pickle
import json
import sys
from argparse import ArgumentParser

from vulcan.data_handling.linguistic_objects.trees.am_tree_as_dict import generate_random_label_alternatives, \
    alignments_from_amtree
from vulcan.server.basic_layout import BasicLayout
from vulcan.server.server import Server
from vulcan.data_handling.data_corpus import from_dict_list
from amconll import parse_amconll


def main():
    parser = ArgumentParser()
    parser.add_argument("pickle_filename", help="Path to the pickle file you want to visualize.")
    parser.add_argument("-pf", "--propbank-frames", type=str,
                        action="store", dest="propbank_frames", default=None,
                        help="Path to a folder containing XML files with Propbank frames, "
                             "such as data/frames/propbank-amr-frames-xml-2018-01-25 in the AMR3.0 corpus. "
                             "If given, vulcan will show frame definitions on node mouseover ")
    parser.add_argument("-wiki", "--show-wikipedia-articles", action="store_true", dest="show_wikipedia_articles",
                        default=False, help="If given, vulcan will show Wikipedia articles on node mouseover."
                                            "Can take quite a while to load in the beginning!")
    parser.add_argument("-p", "--port", type=int, action="store", dest="port", default=5050)
    parser.add_argument("--json", action="store_true", dest="is_json_file", default=False)
    parser.add_argument("--show_node_names", action="store_true", dest="show_node_names", default=False)
    args = parser.parse_args()

    if args.propbank_frames is not None:
        propbank_path = args.propbank_frames + "/"
    else:
        propbank_path = None

    if args.is_json_file:
        with open(args.pickle_filename, "r") as f:
            input_dicts = json.load(f)
    else:
        with open(args.pickle_filename, "rb") as f:
            input_dicts = pickle.load(f)

    # input_dicts = make_highlights_example()

    data_corpus = from_dict_list(input_dicts, propbank_frames_path=propbank_path,
                                 show_wikipedia=args.show_wikipedia_articles)

    layout = BasicLayout(data_corpus.slices.values(), data_corpus.linkers, data_corpus.size)

    print(layout.layout)

    server = Server(layout, port=args.port, show_node_names=args.show_node_names)
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
    main()
