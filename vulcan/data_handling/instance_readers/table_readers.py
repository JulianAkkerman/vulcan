from vulcan.data_handling.instance_readers.instance_reader import InstanceReader
from vulcan.data_handling.visualization_type import VisualizationType


class StringTableInstanceReader(InstanceReader):
    """
    InstanceReader for tables in string form. Assumes each instance is a table of strings (i.e. List[List[str]]).
    """

    def convert_single_instance(self, instance):
        return instance

    def get_visualization_type(self):
        return VisualizationType.TABLE
