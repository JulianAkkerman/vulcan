from data_handling.visualization_type import VisualizationType
from search.graph_nodes.node_content_equals import NodeContentEquals
from search.graph_nodes.outer_graph_node_layer import OuterGraphNodeLayer
from search.table.column_count_at_least import ColumnCountAtLeast
from search.table.outer_table_as_a_whole_layer import OuterTableAsAWholeLayer
from search.table_cells.cell_content_equals import CellContentEquals
from search.table_cells.cell_content_matches import CellContentMatches
from search.table_cells.outer_table_cells_layer import OuterTableCellsLayer

OUTER_SEARCH_LAYERS = {
    "OuterTableCellsLayer": OuterTableCellsLayer(),
    "OuterTableAsAWholeLayer": OuterTableAsAWholeLayer(),
    "OuterGraphNodeLayer": OuterGraphNodeLayer()
}

INNER_SEARCH_LAYERS = {
    "CellContentEquals": CellContentEquals(),
    "CellContentMatches": CellContentMatches(),
    "NodeContentEquals": NodeContentEquals(),
    "ColumnCountAtLeast": ColumnCountAtLeast()
}

OUTER_TO_INNER_SEARCH_LAYERS = {
    "OuterTableCellsLayer": ["CellContentEquals", "CellContentMatches"],
    "OuterTableAsAWholeLayer": ["ColumnCountAtLeast"],
    "OuterGraphNodeLayer": ["NodeContentEquals"]
}

# TODO maybe do different ones for table and string, and for graph and tree
VISUALIZATION_TYPE_TO_OUTER_SEARCH_LAYERS = {
    VisualizationType.TABLE: ["OuterTableCellsLayer", "OuterTableAsAWholeLayer"],
    VisualizationType.GRAPH: ["OuterGraphNodeLayer"],
    VisualizationType.STRING: ["OuterTableCellsLayer", "OuterTableAsAWholeLayer"],
    VisualizationType.TREE: ["OuterGraphNodeLayer"],
    VisualizationType.LINKER: []
}
