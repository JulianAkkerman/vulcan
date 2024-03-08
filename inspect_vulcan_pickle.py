import sys
import pickle


def main():
    pickle_path = sys.argv[1]
    with open(pickle_path, "rb") as f:
        data = pickle.load(f)
    for dictionary in data:
        print_dict(dictionary)


def print_dict(dictionary):
    print("[")
    if "type" in dictionary:
        print(f"type: {dictionary['type']}")
    else:
        print("\ttype: None given, implicitly assumed as 'data'")
    if "name" in dictionary:
        print(f"\tname: {dictionary['name']}")
    for key, value in dictionary.items():
        if key not in ["type", "name", "instances", "scores"]:
            print(f"\t{key}: {value}")
    if "instances" in dictionary:
        print(f"\tHas {len(dictionary['instances'])} instances.")
        if len(dictionary["instances"]) > 0:
            first_instance_beginning = str(dictionary['instances'][0])[:50].replace('\n', ' ')
            print(f"\tFirst one starts with {first_instance_beginning}...")
    if "scores" in dictionary:
        print(f"\tHas {len(dictionary['scores'])} scores.")
        if len(dictionary["scores"]) > 0:
            num_scores_first_instance = len(dictionary['scores'][0])
            print(f"\tFirst one has {num_scores_first_instance} entries.")
            print("\tFor example:")
            for i, entry in enumerate(dictionary['scores'][0]):
                print(f"\t\t{entry}: {dictionary['scores'][0][entry]}")
                if i == 2:
                    break
    print("],")


if __name__ == "__main__":
    main()
