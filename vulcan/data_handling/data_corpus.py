from data_handling.instance_readers.string_instance_reader import StringInstanceReader


class DataCorpus:

    def __init__(self):
        self.size = None
        self.slices = dict()

    @staticmethod
    def from_dict_list(self, data):
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
                    if data_corpus.size != len(entry['data']):
                        raise ValueError(f"Error when creating DataCorpus from dict list: number of instances for"
                                         f"{name} ({len(instances)}) does not match previously seen data.")
                else:
                    data_corpus.size = len(entry['data'])
                    print(f"Retreived DataCorpus size from 'data' entry {name}: {data_corpus.size} instances")

                input_format = entry.get('format', 'string')
                instance_reader = get_instance_reader_by_name(input_format)
                instances = instance_reader.convert_instances(instances)

                label_alternatives = read_data_alternatives(entry)
                data_corpus.add_slice(name, instances, label_alternatives)
            elif entry_type == 'linker':
                pass
            else:
                raise ValueError(f"Error when creating DataCorpus from dict list: unknown entry type '{entry_type}'")

    def add_slice(self, name, instances, label_alternatives=None):
        """
        Add a slice of data to the corpus.
        """
        self.slices[name] = CorpusSlice(name, instances, label_alternatives)


def get_instance_reader_by_name(reader_name):
    """

    :param reader_name:
    :return:
    """
    if reader_name == 'string':
        return StringInstanceReader()


def read_data_alternatives(entry):
    return None


class CorpusSlice:

    def __init__(self, name, instances, label_alternatives=None):
        self.name = name
        self.instances = instances
        self.label_alternatives = label_alternatives