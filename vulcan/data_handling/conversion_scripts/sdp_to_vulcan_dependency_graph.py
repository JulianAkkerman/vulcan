import json

example = """{"tokens" : ["This", "is", "a", "test", "."], "edges": [[3, "BV", 4], [2, "ARG1", 1], [2, "ARG2", 4]]}"""


def sdp_to_vulcan_dependency_graph(sdp_json):

    print(sdp_json["tokens"])
    print(sdp_json["edges"])

    dep_tree = []
    for source, label, target in sdp_json["edges"]:
        # note that source and target are 1-based, but VULCAN expects 0-based
        dep_tree.append((source - 1, target - 1, label))

    print("sentence", [[t] for t in sdp_json["tokens"]])
    print("dep_tree", dep_tree)

    return sdp_json["tokens"], dep_tree


def main():
    sdp_to_vulcan_dependency_graph(json.loads(example))


if __name__ == '__main__':
    main()

