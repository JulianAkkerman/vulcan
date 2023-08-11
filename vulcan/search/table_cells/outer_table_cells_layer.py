from abc import ABC
from typing import List, Any

from search.inner_search_layer import InnerSearchLayer
from search.outer_search_layer import OuterSearchLayer


class OuterTableCellsLayer(OuterSearchLayer):
    def get_description(self) -> str:
        return "This layer checks if any cell in a table matches the given criteria, and highlights the cells that do."

    def get_label(self) -> str:
        return "Any cell in the table matches:"

    def apply(self, inner_search_layers: List[InnerSearchLayer], user_arguments: List[List[str]], object: List[List[str]]):
        for row in object:
            for cell in row:
                for inner_search_layer, user_args in zip(inner_search_layers, user_arguments):
                    if inner_search_layer.apply(cell, user_args):
                        return True


class InnerTableCellsLayer(InnerSearchLayer, ABC):

    def apply(self, obj: str, user_arguments: List[str]):
        raise NotImplementedError()
