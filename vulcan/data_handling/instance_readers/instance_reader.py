from data_handling.visualization_type import VisualizationType


class InstanceReader:

    def convert_instances(self, instances):
        raise NotImplementedError()

    def get_visualization_type(self) -> VisualizationType:
        raise NotImplementedError()
