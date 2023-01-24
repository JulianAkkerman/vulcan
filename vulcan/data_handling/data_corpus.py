from typing import List, Dict
import copy

from data_handling.instance_readers.amr_graph_instance_reader import AMRGraphStringInstanceReader, \
    AMRGraphInstanceReader
from data_handling.instance_readers.amtree_instance_reader import AMTreeInstanceReader, AMTreeStringInstanceReader
from data_handling.instance_readers.string_instance_reader import StringInstanceReader, TokenInstanceReader, \
    TokenizedStringInstanceReader
from data_handling.visualization_type import VisualizationType
from collections import OrderedDict


class DataCorpus:

    def __init__(self, message: str = ""):
        self.size = None
        self.slices = OrderedDict()
        self.linkers = []
        self.message = message

    def add_slice(self, name, instances, visualization_type, label_alternatives=None, highlights=None):
        """
        Add a slice of data to the corpus.
        """
        self.slices[name] = CorpusSlice(name, instances, visualization_type, label_alternatives, highlights)

    def add_linker(self, linker):
        self.linkers.append(linker)


def from_dict(data: Dict) -> DataCorpus:
    """
    Create a DataCorpus object from a dictionary.
    """
    graph_instance_reader = get_instance_reader_by_name('graph')
    gold_instances = graph_instance_reader.convert_instances(data["gold_graphs"])
    gold_highlights = data["highlights"]
    string_instance_reader = get_instance_reader_by_name('string')
    sentences = string_instance_reader.convert_instances(data["sentences"])
    predicted_instances = graph_instance_reader.convert_instances(data["predicted_graphs"])

    data_corpus = DataCorpus(data["message"])
    data_corpus.size = len(gold_instances)
    data_corpus.add_slice("sentences", sentences, VisualizationType.STRING)
    data_corpus.add_slice("predicted", predicted_instances, VisualizationType.GRAPH)
    data_corpus.add_slice("gold", gold_instances, VisualizationType.GRAPH, highlights=gold_highlights)

    return data_corpus


def get_instance_reader_by_name(reader_name):
    """

    :param reader_name:
    :return:
    """
    if reader_name == 'string':
        return StringInstanceReader()
    elif reader_name == 'token':
        return TokenInstanceReader()
    elif reader_name == 'tokenized_string':
        return TokenizedStringInstanceReader()
    elif reader_name == 'amtree':
        return AMTreeInstanceReader()
    elif reader_name == 'amtree_string':
        return AMTreeStringInstanceReader()
    elif reader_name == 'graph':
        return AMRGraphInstanceReader()
    elif reader_name == 'graph_string':
        return AMRGraphStringInstanceReader()


def read_label_alternatives(corpus_entry):
    """
    Creates a copy of the 'label_alternatives' entry in corpus_entry, where each label alternative has been
    processed by the appropriate InstanceReader.
    :param corpus_entry: An input corpus entry of type 'data'.
    :return: That created copy
    """
    if 'label_alternatives' in corpus_entry:
        label_alternatives = corpus_entry['label_alternatives']
        assert_is_list(label_alternatives)
        ret = []
        for label_alternative_instance in label_alternatives:
            assert_is_dict(label_alternative_instance)
            ret_instance = {}
            for node_name, node_label_alternatives in label_alternative_instance.items():
                ret_node = []
                assert_is_list(node_label_alternatives)
                for node_label_alternative in node_label_alternatives:
                    assert_is_dict(node_label_alternative)

                    ret_alt = copy.deepcopy(node_label_alternative)
                    instance_reader = get_instance_reader_by_name(ret_alt['format'])
                    ret_alt['label'] = instance_reader.convert_single_instance(ret_alt['label'])
                    ret_alt['format'] = instance_reader.get_visualization_type()
                    ret_node.append(ret_alt)
                ret_instance[node_name] = ret_node
            ret.append(ret_instance)
        return ret
    else:
        return None


def assert_is_dict(possible_dictionary):
    if not isinstance(possible_dictionary, dict):
        raise ValueError(f"Error: object must be a dict, "
                         f"but was {type(possible_dictionary)}")


def assert_is_list(possible_list):
    if not isinstance(possible_list, list):
        raise ValueError(f"Error: object must be a list, "
                         f"but was {type(possible_list)}")


class CorpusSlice:

    def __init__(self,
                 name: str,
                 instances: List,
                 visualization_type: VisualizationType,
                 label_alternatives=None,
                 highlights=None):
        self.name = name
        self.instances = instances
        self.visualization_type = visualization_type
        self.label_alternatives = label_alternatives
        self.highlights = highlights
