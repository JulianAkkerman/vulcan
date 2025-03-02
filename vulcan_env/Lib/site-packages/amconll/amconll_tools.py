#
# Copyright (c) 2020 Saarland University.
#
# This file is part of AM Parser
# (see https://github.com/coli-saar/am-parser/).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from typing import List, Dict, Tuple, Iterable, Union

from dataclasses import dataclass

"""
This is mostly a copy of the same class in am-parser.
"""


@dataclass(frozen=True)
class Entry:
    token: str
    replacement: str
    lemma: str
    pos_tag: str
    ner_tag: str
    fragment: str
    lexlabel: str
    typ: str
    head: int
    label: str
    aligned: bool
    range: Union[str, None]

    def __iter__(self):
        return iter([self.token, self.replacement, self.lemma, self.pos_tag, self.ner_tag, self.fragment, self.lexlabel,
                     self.typ, self.head, self.label, self.aligned, self.range])

    def set_head(self, head: int) -> "Entry":
        return Entry(self.token, self.replacement, self.lemma, self.pos_tag, self.ner_tag, self.fragment, self.lexlabel,
                     self.typ, head, self.label, self.aligned, self.range)

    def set_edge_label(self, edge_label: str) -> "Entry":
        return Entry(self.token, self.replacement, self.lemma, self.pos_tag, self.ner_tag, self.fragment, self.lexlabel,
                     self.typ, self.head, edge_label, self.aligned, self.range)

    def set_lexlabel(self, lexlabel: str) -> "Entry":
        return Entry(self.token, self.replacement, self.lemma, self.pos_tag, self.ner_tag, self.fragment, lexlabel,
                     self.typ, self.head, self.label, self.aligned, self.range)

    def set_fragment(self, fragment: str) -> "Entry":
        return Entry(self.token, self.replacement, self.lemma, self.pos_tag, self.ner_tag, fragment, self.lexlabel,
                     self.typ, self.head, self.label, self.aligned, self.range)

    def set_typ(self, typ: str) -> "Entry":
        return Entry(self.token, self.replacement, self.lemma, self.pos_tag, self.ner_tag, self.fragment, self.lexlabel,
                     typ, self.head, self.label, self.aligned, self.range)


@dataclass
class AMSentence:
    """Represents a sentence"""
    words: List[Entry]
    attributes: Dict[str, str]

    def __iter__(self):
        return iter(self.words)

    def __index__(self, i):
        """Zero-based indexing."""
        return self.words[i]

    def get_tokens(self, shadow_art_root) -> List[str]:
        r = [word.token for word in self.words]
        if shadow_art_root and r[-1] == "ART-ROOT":
            r[-1] = "."
        return r

    def get_replacements(self) -> List[str]:
        return [word.replacement for word in self.words]

    def get_pos(self) -> List[str]:
        return [word.pos_tag for word in self.words]

    def get_lemmas(self) -> List[str]:
        return [word.lemma for word in self.words]

    def get_ner(self) -> List[str]:
        return [word.ner_tag for word in self.words]

    def get_supertags(self) -> List[str]:
        return [word.fragment + "--TYPE--" + word.typ for word in self.words]

    def get_lexlabels(self) -> List[str]:
        return [word.lexlabel for word in self.words]

    def get_ranges(self) -> List[str]:
        return [word.range for word in self.words]

    def get_heads(self) -> List[int]:
        return [word.head for word in self.words]

    def get_edge_labels(self) -> List[str]:
        return [word.label if word.label != "_" else "IGNORE" for word in
                self.words]  # this is a hack :(, which we need because the dev data contains _

    def set_lexlabels(self, labels: List[str]) -> "AMSentence":
        assert len(labels) == len(
            self.words), f"number of lexical labels must agree with number of words but got {len(labels)} " \
                         f"and {len(self.words)}"
        return AMSentence(
            [Entry(word.token, word.replacement, word.lemma, word.pos_tag, word.ner_tag, word.fragment, labels[i],
                   word.typ, word.head, word.label, word.aligned, word.range)
             for i, word in enumerate(self.words)], self.attributes)

    def set_heads(self, heads: List[int]) -> "AMSentence":
        assert len(heads) == len(
            self.words), f"number of heads must agree with number of words but got {len(heads)} and {len(self.words)}"
        assert all(0 <= h <= len(self.words) for h in
                   heads), f"heads must be in range 0 to {len(self.words)} but got heads {heads}"

        return AMSentence(
            [Entry(word.token, word.replacement, word.lemma, word.pos_tag, word.ner_tag, word.fragment, word.lexlabel,
                   word.typ, heads[i], word.label, word.aligned, word.range)
             for i, word in enumerate(self.words)], self.attributes)

    @staticmethod
    def get_bottom_supertag() -> str:
        return "_--TYPE--_"

    # noinspection PyTypeChecker
    @staticmethod
    def split_supertag(supertag: str) -> Tuple[str, str]:
        return tuple(supertag.split("--TYPE--", maxsplit=1))

    def attributes_to_list(self) -> List[str]:
        return [f"#{key}:{val}" for key, val in self.attributes.items()]

    def check_validity(self):
        """Checks if representation makes sense, doesn't do AM algebra type checking"""
        assert len(self.words) > 0, "Sentence is empty"
        for entry in self.words:
            assert entry.head in range(len(self.words) + 1), f"head of {entry} is not in sentence range"
        has_root = any(w.label == "ROOT" and w.head == 0 for w in self.words)
        if not has_root:
            assert all((w.label == "IGNORE" or w.label == "_") and w.head == 0 for w in
                       self.words), f"Sentence doesn't have a root but seems annotated with trees:\n {self}"

    def __str__(self):
        r = []
        if self.attributes:
            r.append("\n".join(f"#{attr}:{val}" for attr, val in self.attributes.items()))
        for i, w in enumerate(self.words, 1):
            fields = list(w)
            if fields[-1] is None:
                fields = fields[:-1]  # when token range not present -> remove it
            r.append("\t".join([str(x) for x in [i] + fields]))
        return "\n".join(r)

    def is_annotated(self):
        return not all((w.label == "_" or w.label == "IGNORE") and w.head == 0 for w in self.words)

    def __len__(self):
        return len(self.words)

    def strip_annotation(self) -> "AMSentence":
        return AMSentence([Entry(word.token, word.replacement, word.lemma, word.pos_tag, word.ner_tag, "_", "_",
                                 "_", 0, "IGNORE", word.aligned, word.range)
                           for word in self.words], self.attributes)


def from_raw_text(rawstr: str, words: List[str], add_art_root: bool, attributes: Dict, contract_ne: bool) -> AMSentence:
    """
    Create an AMSentence from raw text, without token ranges and stuff
    :param rawstr:
    :param words:
    :param add_art_root:
    :param attributes:
    :param contract_ne: shall we contract named entites, e.g. Barack Obama --> Barack_Obama. Should be done only for AMR.
    :return:
    """
    entries = []
    # use spacy lemmas and tags
    from graph_dependency_parser.components.spacy_interface import run_spacy, lemma_postprocess, ne_postprocess, \
        is_number

    spacy_doc = run_spacy([words])
    ne = []
    for i in range(len(words)):
        word = words[i]
        lemma = lemma_postprocess(word, spacy_doc[i].lemma_)
        if contract_ne:
            if spacy_doc[i].ent_type_ not in ["QUANTITY", "PERCENT", "CARDINAL", "MONEY"]:
                if spacy_doc[i].ent_iob_ == "B":
                    if len(ne) > 0:
                        ent_typ = ne_postprocess(spacy_doc[i - 1].ent_type_)
                        e = Entry("_".join(ne), is_number(ent_typ),
                                  lemma_postprocess(words[i - 1], spacy_doc[i - 1].lemma_), spacy_doc[i - 1].tag_, "O",
                                  "_", "_", "_", 0, "IGNORE", True, None)
                        entries.append(e)
                    ne = [word]
                elif spacy_doc[i].ent_iob_ == "I":
                    ne.append(word)

            if len(ne) > 0:
                if i == len(words) - 1 or i + 1 < len(words) and spacy_doc[i + 1].ent_iob_ != "I":
                    ent_typ = ne_postprocess(spacy_doc[i].ent_type_)

                    e = Entry("_".join(ne), is_number(ent_typ), lemma, spacy_doc[i].tag_, "O", "_", "_", "_", 0,
                              "IGNORE", True, None)
                    entries.append(e)
                    ne = []
            else:
                # ne_postprocess(spacy_doc[i].ent_type_)
                replacement = "_" if word == word.lower() else word.lower()
                e = Entry(word, replacement, lemma, spacy_doc[i].tag_, "O", "_", "_", "_", 0, "IGNORE", True,
                          None)
                entries.append(e)

        else:  # don't contract NEs
            # ne_postprocess(spacy_doc[i].ent_type_)
            replacement = "_" if word == word.lower() else word.lower()
            e = Entry(word, replacement, lemma, spacy_doc[i].tag_, "O", "_", "_", "_", 0, "IGNORE", True,
                      None)
            entries.append(e)

    if add_art_root:
        entries.append(
            Entry("ART-ROOT", "_", "ART-ROOT", "ART-ROOT", "ART-ROOT", "_", "_", "_", 0, "IGNORE", True, None))
    attributes["raw"] = rawstr
    sentence = AMSentence(entries, attributes)
    sentence.check_validity()
    return sentence


def parse_amconll(fil, validate: bool = True) -> Iterable[AMSentence]:
    """
    Reads a file and returns a generator over AM sentences.
    :param validate:
    :param fil:
    :return:
    """
    expect_header = True
    new_sentence = True
    entries = []
    attributes = dict()
    for line in fil:
        line = line.rstrip("\n")
        if line.strip() == "":
            # sentence finished
            if len(entries) > 0:
                sent = AMSentence(entries, attributes)
                if validate:
                    sent.check_validity()
                yield sent
            new_sentence = True

        if new_sentence:
            expect_header = True
            attributes = dict()
            entries = []
            new_sentence = False
            if line.strip() == "":
                continue

        if expect_header:
            if line.startswith("#"):
                key, val = line[1:].split(":", maxsplit=1)
                attributes[key] = val
            else:
                expect_header = False

        if not expect_header:
            fields = line.split("\t")
            assert len(fields) == 12 or len(fields) == 13
            if len(fields) == 12:  # id + entry but no token ranges
                entries.append(
                    Entry(fields[1], fields[2], fields[3], fields[4], fields[5], fields[6], fields[7], fields[8],
                          int(fields[9]), fields[10], bool(fields[11]), None))
            elif len(fields) == 13:
                entries.append(
                    Entry(fields[1], fields[2], fields[3], fields[4], fields[5], fields[6], fields[7], fields[8],
                          int(fields[9]), fields[10], bool(fields[11]), fields[12]))


def write_conll(file_name: str, sentences: Iterable[AMSentence]):
    """
    Takes a file object and an iterable of AMSentence and writes all the AM sentences to the file, in the .amconll format
    :param file_name: where to write the file
    :param sentences: the sentences to write into the amconll file.
    :return:
    """
    with open(file_name, 'w') as f:
        for sentence in sentences:
            f.write(str(sentence))
            f.write('\n\n')


def reorder_amconll(amr_corpus, amconll_file, output_path):
    """
    Re-orders an amconll file to match an AMR corpus file
    Note: requires the penman library (pip install penman)
    :param amr_corpus: an AMR corpus file with IDs
    :param amconll_file: an amconll file with IDs
    :param output_path: where to write the new amconll file
    """

    import penman
    amrs = penman.load(amr_corpus)

    # get the amconll entries
    amconll_file_connection = open(amconll_file, 'r')
    amconll_generator = parse_amconll(amconll_file_connection)
    amconll_entries = list(amconll_generator)
    amconll_file_connection.close()

    new_amconll = []
    for amr in amrs:
        id = amr.metadata["id"]
        # inefficiently find the matching sentence from the amconll file
        for entry in amconll_entries:
            if id == entry.attributes["id"]:
                new_amconll.append(entry)

    write_conll(output_path, new_amconll)
