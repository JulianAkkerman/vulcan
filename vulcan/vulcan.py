import penman

from server.basic_layout import BasicLayout
from server.server import Server
from data_handling.data_corpus import from_dict_list

if __name__ == "__main__":

    input_dicts = [
        {
            "type": "data",
            "name": "test",
            "instances": ["abc", "sfjisdl", "my name is bob"],
            "format": "string"
        }
    ]

    data_corpus = from_dict_list(input_dicts)

    print(data_corpus.slices["test"].instances)

    layout = BasicLayout(data_corpus.slices.values())

    print(layout.layout)

    # graphs = penman.load("C:/Users/jonas/Documents/Work/data/Edinburgh/amr3.0/data/amrs/split/dev/"
    #                      "amr-release-3.0-amrs-dev-bolt.txt")
    #
    # print(len(graphs))
    # print(graphs[0])
    #
    # server = Server(graphs)
    # server.start()


