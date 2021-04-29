#!/usr/bin/env python3

from re import findall
from typing import List

from dataclasses import dataclass
from exceptions import UnknownFileTypeError
from numpy import float64
from pandas import DataFrame


@dataclass(frozen=True)
class Dataset:
    file_name: str
    file_type: str
    cols: List[str]

    def _row_regex(self) -> str:
        number = r"[\d.,eE-]+"
        fields = [f"({number})"] * len(self.cols)
        row = "\t".join(fields)
        return row

    def load(self) -> DataFrame:
        if self.file_type == "Perkin Elmer":
            encoding = "iso-8859-1"
        elif self.file_type == "TSV":
            encoding = "utf-8"
        else:
            raise UnknownFileTypeError(self.file_type)
        with open(self.file_name, "r", encoding=encoding) as file:
            file_str = file.read()
            regex = self._row_regex()
            rows = findall(regex, file_str)
            df = DataFrame(rows, columns=self.cols, dtype=float64)
            return df
