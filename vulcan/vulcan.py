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
        },
        {
            "type": "data",
            "name": "test2",
            "instances": ["1", "2", "3"],
            "format": "string"
        },
        {
            "type": "data",
            "name": "test3",
            "instances": ["ayaya", "what", "is up"],
            "format": "string"
        }
    ]

    data_corpus = from_dict_list(input_dicts)

    print(data_corpus.slices["test3"].instances)

    layout = BasicLayout(data_corpus.slices.values())

    print(layout.layout)

    server = Server(layout)
    server.start()  # at this point, the server is running on this thread, and nothing below will be executed




