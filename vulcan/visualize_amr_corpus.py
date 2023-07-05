import pickle
import sys
from argparse import ArgumentParser

import penman

from data_handling.linguistic_objects.trees.am_tree_as_dict import generate_random_label_alternatives, \
    alignments_from_amtree
from server.basic_layout import BasicLayout
from server.server import Server
from data_handling.data_corpus import from_dict_list
from data_handling.format_names import FORMAT_NAME_STRING, FORMAT_NAME_GRAPH
from amconll import parse_amconll


def main():
    parser = ArgumentParser()
    parser.add_argument("corpus_filename", help="Path to the AMR corpus file you want to visualize.")
    parser.add_argument("-pf", "--propbank-frames", type=str,
                        action="store", dest="propbank_frames", default=None,
                        help="Path to a folder containing XML files with Propbank frames, "
                             "such as data/frames/propbank-amr-frames-xml-2018-01-25 in the AMR3.0 corpus. "
                             "If given, vulcan will show frame definitions on node mouseover ")
    parser.add_argument("-wiki", "--show-wikipedia-articles", action="store_true", dest="show_wikipedia_articles",
                        default=False, help="If given, vulcan will show Wikipedia articles on node mouseover."
                                            "Can take quite a while to load in the beginning!")
    args = parser.parse_args()

    penman_corpus = penman.load(args.corpus_filename)

    print(penman_corpus[0].metadata.keys())
    print(penman_corpus[0].metadata["snt"])

    graphs = []
    sentences = []
    for graph in penman_corpus:
        graphs.append(graph)
        sentences.append(graph.metadata["snt"])

    input_dicts = [
        {
            "type": "data",
            "name": "graphs",
            "instances": graphs,
            "format": FORMAT_NAME_GRAPH
        },
        {
            "type": "data",
            "name": "sentences",
            "instances": sentences,
            "format": FORMAT_NAME_STRING
        },
    ]

    data_corpus = from_dict_list(input_dicts, propbank_frames_path=args.propbank_frames,
                                 show_wikipedia=args.show_wikipedia_articles)

    layout = BasicLayout(data_corpus.slices.values(), data_corpus.linkers, data_corpus.size)

    print(layout.layout)

    server = Server(layout)
    server.start()  # at this point, the server is running on this thread, and nothing below will be executed


if __name__ == '__main__':
    main()
