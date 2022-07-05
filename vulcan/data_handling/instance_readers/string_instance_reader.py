from data_handling.instance_readers.instance_reader import InstanceReader
from data_handling.visualization_type import VisualizationType


class StringInstanceReader(InstanceReader):
    """
    InstanceReader for string data. Assumes each instance is a string, and splits it along spaces to obtain a string
    list internally.
    """

    def convert_instances(self, instances):
        return [instance.split(" ") for instance in instances]

    def get_visualization_type(self):
        return VisualizationType.STRING
