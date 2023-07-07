from nltk import Tree

from vulcan.pickle_builder.pickle_builder import PickleBuilder


def make_nltk_example():
    pb = PickleBuilder({'Sentence': 'string', 'Tree': 'nltk_tree'})
    pb.add_instance_by_name('Tree', Tree.fromstring('(S (NP (D the) (N dog)) (VP (V chased) (NP (D the) (N cat))))'))
    pb.add_instance_by_name('Sentence', 'The dog chased the cat.')
    pb.add_instance_by_name('Tree', Tree.fromstring('(S (NP (D the) (N cat)) (VP (V chased) (NP (D the) (N dog))))'))
    pb.add_instance_by_name('Sentence', 'The cat chased the dog.')
    pb.write("nltk_example.pickle")


def make_nltk_json_example():
    pb = PickleBuilder({'Sentence': 'string', 'Tree': 'nltk_tree_string'})
    pb.add_instance_by_name('Tree', '(S (NP (D the) (N dog)) (VP (V chased) (NP (D the) (N cat))))')
    pb.add_instance_by_name('Sentence', 'The dog chased the cat.')
    pb.add_instance_by_name('Tree', '(S (NP (D the) (N cat)) (VP (V chased) (NP (D the) (N dog))))')
    pb.add_instance_by_name('Sentence', 'The cat chased the dog.')
    pb.write_as_json("nltk_example.json")

def main():
    make_nltk_json_example()


if __name__ == '__main__':
    main()