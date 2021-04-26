#!/usr/bin/env python3

from re import findall

from exceptions import UnknownFileTypeError
from numpy import float64
from pandas import DataFrame


class Dataset:
    def __init__(self, file_name, file_type, cols):
        self.file_name = file_name
        self.file_type = file_type
        self.cols = cols

    def _row_regex(self):
        number = r"[\d.,eE-]+"
        fields = [f"({number})"] * len(self.cols)
        row = "\t".join(fields)
        return row

    def load(self):
        if self.file_type == "perkin_elmer":
            encoding = "iso-8859-1"
        elif self.file_type == "tsv":
            encoding = "utf-8"
        else:
            raise UnknownFileTypeError(self.file_type)
        with open(self.file_name, "r", encoding=encoding) as file:
            file_str = file.read()
            regex = self._row_regex()
            rows = findall(regex, file_str)
            df = DataFrame(rows, columns=self.cols, dtype=float64)
            return df
