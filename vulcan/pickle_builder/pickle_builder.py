import pickle
import json
from typing import Dict, Any, Tuple, List

from data_handling.format_names import FORMAT_NAME_STRING, FORMAT_NAME_TOKENIZED_STRING, FORMAT_NAME_TOKEN, \
    FORMAT_NAME_OBJECT_TABLE, FORMAT_NAME_STRING_TABLE


class PickleBuilder:
    def __init__(self, name_to_format: Dict[str, str]):
        """
        :param name_to_format: For each thing you want to visualize (e.g. sentence, graph, tree), choose a name. You
         can choose any arbitrary name such as "Gold sentence" or "Input sentence" or "Predicted graph" or "tree 2".
         Now for each name, choose a format from the ones in vulcan.data_handling.format_names. For example, if you
         want to visualize an input sentence and a predicted graph, and you give the input sentence as a string and
         the graph in penman format, the name_to_format dictionary could look like this:
            {'Input sentence': 'string', 'Predicted graph': 'graph'}
         For data that is not just its own thing, such as dependency trees, linkers or node label alternatives,
         add them after the constructor with the respective "setup" methods.
        """
        self.data = dict()
        for name, format in name_to_format.items():
            self.data[name] = dict({
                'type': 'data',
                'format': format,
                'instances': []
            })

    def setup_dependency_tree(self, linked_name: str):
        """
        Sets up the pickle builder to receive dependency trees; call this after the constructor, before adding any
        instances.
        :param linked_name: The name of the string or table (e.g. tagged string) data that the dependency trees span.
        For example, if your name_to_format dictionary in the constructor contained 'Input sentence': 'string', then
        'Input sentence' would be a valid choice for linked_name here.
        :return: None
        """
        assert linked_name in self.data
        assert self.data[linked_name]['type'] == 'data'
        assert self.data[linked_name]['format'] in [FORMAT_NAME_STRING, FORMAT_NAME_TOKEN, FORMAT_NAME_TOKENIZED_STRING,
                                                    FORMAT_NAME_STRING_TABLE, FORMAT_NAME_OBJECT_TABLE]
        self.data[linked_name]["dependency_trees"] = []

    def add_instances_by_name(self, name_to_instance: Dict[str, Any], run_checks: bool = True):
        """
        Adds one corpus instance, including all its parts (graphs, sentences, trees, etc.) to the pickle builder.
        :param name_to_instance: Must contain entries for all names that were set up (via the constructor or
            one of the setup methods) and only those names.
        :param run_checks: If false, the condition on name_to_instance is not checked. If true, if the condition is
            not met, an AssertionError is raised.
        :return: None
        """
        if run_checks:
            names_match_data_structure = set(name_to_instance.keys()) == set(self.data.keys())
            assert names_match_data_structure
            assert self._instance_counts_are_in_sync()
        for name, instance in name_to_instance.items():
            self._add_instance_to_data(name, instance)

    def _add_instance_to_data(self, name: str, instance: Any):
        self.data[name]['instances'].append(instance)

    def add_instance_by_name(self, name: str, instance: Any, run_checks: bool = True):
        """
        Adds one part of a corpus instance, i.e. one graph, sentence, tree, etc. to the pickle builder.

        This method assumes that all instances are added synchronously, i.e. that for each name, one instance is added,
        and then again for each name, one instance is added, and so on. This is enforced in the method, and will raise
        an AssertionError if violated (to help you catch the situation where you accidentally get out of synch). If you
        are adding the instances in a different order, set run_checks to False.

        :param name: The name of the data structure, as given to the constructor or one of the setup methods.
        :param instance: The instance to be added
        :param run_checks: See main docstring text of this method.
        :return:
        """
        if run_checks:
            assert name in self.data
            min_number_of_instances_in_data = min(self._get_all_instance_counts())
            addition_will_break_sync = len(self.data[name]['instances']) > min_number_of_instances_in_data
            assert not addition_will_break_sync
        self._add_instance_to_data(name, instance)

    def _get_all_instance_counts(self):
        return [len(d['instances']) for d in self.data.values()]

    def _instance_counts_are_in_sync(self):
        return len(set(self._get_all_instance_counts())) == 1

    def add_dependency_tree_by_name(self,
                                    linked_name: str,
                                    dependency_tree: List[Tuple[int, int, str]],
                                    run_checks: bool = True):
        """

        :param linked_name: The table or string to add this dependency tree to. See setup_dependency_tree.
        :param dependency_tree: A list of dependency edges, with each edge being a triple (source, target, label).
            Source and target are 0-indexed, and label is a string.
        :param run_checks: If true, will check that adding this will not put the data out of sync.
        :return:
        """
        instances = self.data[linked_name]['instances']
        dependency_trees = self.data[linked_name]['dependency_trees']
        if run_checks:
            assert len(dependency_trees) <= len(instances)
        dependency_trees.append(dependency_tree)

    def _make_data_for_pickle(self, run_checks: bool = True):
        if run_checks:
            assert self._instance_counts_are_in_sync()
        data_for_pickle = []
        for name, data in self.data.items():
            # create new dict that also includes {'name': name}
            data_for_pickle.append(dict(data, name=name))
        return data_for_pickle

    def write(self, pickle_path: str):
        """
        :param pickle_path: Path to the pickle file that will be created.
        """
        data_for_pickle = self._make_data_for_pickle()
        with open(pickle_path, 'wb') as f:
            pickle.dump(data_for_pickle, f)

    def write_as_json(self, json_path: str):
        """
        :param json_path: Path to the json file that will be created.
        """
        data_for_pickle = self._make_data_for_pickle()
        with open(json_path, 'w') as f:
            json.dump(data_for_pickle, f)


def main():
    pb = PickleBuilder({'Sentence': 'string', 'Graph': 'graph_string'})
    pb.add_instances_by_name({'Sentence': 'This is a test sentence.',
                              'Graph': '(s / sentence :domain (t / this) :mod (t2 / test))'})


    try:
        pb.add_instances_by_name({'Sentence': 'This is a test sentence that is missing a graph.'})
        raise Exception('Checks for correct set of names when adding multiple instances failed.')
    except AssertionError:
        pass


    try:
        pb.add_instances_by_name({'Sentence': 'This is a test sentence.',
                                  'Graph': 'This is a test sentence.',
                                  'Sentence2': 'This is a test sentence that is too much.'})
        raise Exception('Checks for correct set of names when adding multiple instances failed.')
    except AssertionError:
        pass

    pb.add_instance_by_name('Sentence', 'This is another test sentence.')
    try:
        pb.write("test.pickle")
        raise Exception('Checks for writing failed.')
    except AssertionError:
        pass

    try:
        pb.add_instance_by_name('Sentence', 'This is another test sentence.')
        raise Exception('Asynchronicity checks for adding single instance failed.')
    except AssertionError:
        pass

    try:
        pb.add_instances_by_name({'Sentence': 'This is a test sentence.',
                                  'Graph': '(s / sentence :domain (t / this) :mod (t2 / test))'})
        raise Exception('Asynchronicity checks for adding multiple instances failed.')
    except AssertionError:
        pass

    pb.add_instance_by_name('Graph', '(s / sentence :domain (t / this) :mod (t2 / test) :mod (a / another))')

    pb.write("test.pickle")


if __name__ == '__main__':
    main()
