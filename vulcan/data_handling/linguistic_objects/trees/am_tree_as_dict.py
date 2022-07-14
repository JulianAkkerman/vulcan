import io
import re

from am_parser.graph_dependency_parser.components.dataset_readers.amconll_tools import AMSentence, Entry, parse_amconll

from data_handling.linguistic_objects.graphs.graph_as_dict import add_child, create_node, create_root, ROOT_EDGE_LABEL
from data_handling.linguistic_objects.graphs.penman_converter import from_penman_graph
from penman import decode

ADDRESS_SEPARATOR = "."
SOURCE_PATTERN = re.compile(r"(?P<source><[a-zA-Z0-9]+>)")

def from_amtree(amtree: AMSentence):
    root_entry = None
    root_id = None
    for i, entry in enumerate(amtree.words):
        if entry.label == ROOT_EDGE_LABEL:
            root_entry = entry
            root_id = i + 1  # IDs in AMSentence are 1-based
            break
    if root_entry is None:
        print(amtree)
        raise Exception("No root entry found in AMSentence")
    address = ""
    return _from_amtree_entry(root_entry, root_id, amtree, address, None)


def _from_amtree_entry(entry, entry_id, amtree, address, parent_in_result):
    node_label = entry.fragment.replace("--LEX--", entry.lexlabel)
    print(node_label)
    node_label = node_label.replace("<root>", "")
    node_label = SOURCE_PATTERN.sub(r" / \g<source>", node_label)
    print(node_label)
    node_label = from_penman_graph(decode(node_label))
    print(node_label)
    if parent_in_result is None:
        result = create_root(address, node_label, label_type="GRAPH")
    else:
        result = add_child(parent_in_result, address, node_label, entry.label, child_label_type="GRAPH")
    children_in_amtree = []
    for i, potential_child in enumerate(amtree):
        if potential_child.head == entry_id:
            children_in_amtree.append((i + 1, potential_child))
    for i, (child_id, child) in enumerate(children_in_amtree):
        child_address = address + ADDRESS_SEPARATOR + str(i)
        _from_amtree_entry(child, child_id, amtree, child_address, result)
    return result


def from_string(string):
    return from_amtree(next(iter(parse_amconll(io.StringIO(string+"\n\n")))))
