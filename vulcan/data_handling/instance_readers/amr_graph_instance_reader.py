from data_handling.instance_readers.instance_reader import InstanceReader
from data_handling.visualization_type import VisualizationType
from data_handling.linguistic_objects.graphs.penman_converter import from_penman_graph
from penman import decode


class AMRGraphInstanceReader(InstanceReader):
    """
    InstanceReader for AMR graphs. Specifically, expects the instances to be in the graph format of the penman library.
    """

    def convert_instances(self, instances):
        return [from_penman_graph(instance) for instance in instances]

    def get_visualization_type(self):
        return VisualizationType.GRAPH


class AMRGraphStringInstanceReader(InstanceReader):
    """
    InstanceReader for AMR graphs. Specifically, expects the instances to be string linearizations of the AMRs, as they
    would occur in the AMR corpus.
    """

    def convert_instances(self, instances):
        return [from_penman_graph(decode(instance)) for instance in instances]

    def get_visualization_type(self):
        return VisualizationType.TREE
