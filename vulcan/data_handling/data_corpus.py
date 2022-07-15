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

    def __init__(self):
        self.size = None
        self.slices = OrderedDict()
        self.linkers = []

    def add_slice(self, name, instances, visualization_type, label_alternatives=None):
        """
        Add a slice of data to the corpus.
        """
        self.slices[name] = CorpusSlice(name, instances, visualization_type, label_alternatives)

    def add_linker(self, linker):
        self.linkers.append(linker)


def from_dict_list(data: List[Dict]) -> DataCorpus:
    """
    Create a DataCorpus object from a dictionary.
    """
    data_corpus = DataCorpus()
    for entry in data:
        entry_type = entry.get('type', 'data')  # default to data
        if entry_type == 'data':

            name = entry['name']
            if not name:
                raise ValueError('Error when creating DataCorpus from dict list: "name" entry is required for'
                                 '"data" type dictionaries')
            instances = entry['instances']
            if not instances:
                raise ValueError('Error when creating DataCorpus from dict list: "instances" entry is required for'
                                 '"data" type dictionaries')

            if data_corpus.size:
                if data_corpus.size != len(entry['instances']):
                    raise ValueError(f"Error when creating DataCorpus from dict list: number of instances for"
                                     f"{name} ({len(instances)}) does not match previously seen data.")
            else:
                data_corpus.size = len(entry['instances'])
                print(f"Retreived DataCorpus size from 'data' entry {name}: {data_corpus.size} instances")

            input_format = entry.get('format', 'string')
            instance_reader = get_instance_reader_by_name(input_format)
            instances = instance_reader.convert_instances(instances)

            label_alternatives = read_label_alternatives(entry)
            data_corpus.add_slice(name, instances, instance_reader.get_visualization_type(), label_alternatives)
        elif entry_type == 'linker':
            # TODO: some sanity check that the linker refers to only existing names (but we may not have seen them yet, so check later?)
            data_corpus.add_linker(entry)
        else:
            raise ValueError(f"Error when creating DataCorpus from dict list: unknown entry type '{entry_type}'")
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
        check_is_list(label_alternatives)
        ret = []
        for label_alternative_instance in label_alternatives:
            check_is_dict(label_alternative_instance)
            ret_instance = {}
            for node_name, node_label_alternatives in label_alternative_instance.items():
                ret_node = []
                check_is_list(node_label_alternatives)
                for node_label_alternative in node_label_alternatives:
                    check_is_dict(node_label_alternative)

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


def check_is_dict(object):
    if not isinstance(object, dict):
        raise ValueError(f"Error: object must be a dict, "
                         f"but was {type(object)}")


def check_is_list(object):
    if not isinstance(object, list):
        raise ValueError(f"Error: object must be a list, "
                         f"but was {type(object)}")


class CorpusSlice:

    def __init__(self,
                 name: str,
                 instances: List,
                 visualization_type: VisualizationType,
                 label_alternatives=None):
        self.name = name
        self.instances = instances
        self.visualization_type = visualization_type
        self.label_alternatives = label_alternatives
