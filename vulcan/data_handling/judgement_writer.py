import csv
import os

from data_handling.data_corpus import DataCorpus


class JudgementWriter:

    def __init__(self, pickle_path: str):

        self.tsv_path = pickle_path + ".judgements.tsv"
        self.rows = []

    def load_from_file_if_exists_else_init_rows(self, corpus: DataCorpus):
        if os.path.isfile(self.tsv_path):
            with open(self.tsv_path, "r") as tsv_file:
                reader = csv.reader(tsv_file, delimiter="\t")
                self.rows = [row for row in reader]
                assert len(self.rows) == corpus.size + 1
        else:
            self.rows = [["judgement_left", "judgement_right", "preference", "comment"]]
            for i in range(corpus.size):
                self.rows.append(["", "", "", ""])

    def log_judgement(self, id_in_corpus: int, judgement_left: str = "", judgement_right: str = "",
                      preference: str = "", comment: str = ""):
        self.rows[id_in_corpus + 1] = [judgement_left, judgement_right, preference, comment]
        with open(self.tsv_path, "w") as tsv_file:
            writer = csv.writer(tsv_file, delimiter="\t")
            writer.writerows(self.rows)
