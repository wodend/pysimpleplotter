#!/usr/bin/env python3

from dataclasses import dataclass
from re import match, search
from typing import List, Tuple

from numpy import float64
from pandas import DataFrame

from pysimpleplotter.exceptions import UnknownFileTypeError


@dataclass(frozen=True)
class Dataset:
    name: str
    file_name: str

    def _dsvs(self, line: str) -> Tuple[str, ...]:
        field_regex = r"[^\s]+"
        sep_regex = r"[\s,]+?"
        dsvs = ()
        capture_field_regex = f"({field_regex})"
        _match = search(capture_field_regex, line)
        _line = line
        while _match:
            dsvs += (_match.group(1),)
            _line = _line[_match.end() :]
            _match = match(sep_regex + capture_field_regex, _line)
        return dsvs

    def _is_header(self, line: str) -> bool:
        header_regex = r"[^\d\W]{2}"
        for value in line:
            if search(header_regex, value) and value.lower() != "nan":
                return True
        return False

    def load(self) -> DataFrame:
        # TODO: Detect when we need iso-8859-1 encoding with libmagic
        with open(self.file_name, "r", encoding="iso-8859-1") as file:
            raw_dsv = []
            for line in file:
                dsvs = self._dsvs(line)
                raw_dsv.append(dsvs)
            col_count = len(raw_dsv[-1])  # Use the last DSV line for col count
            dsv = [values for values in raw_dsv if len(values) == col_count]
            if self._is_header(dsv[0]):
                cols = dsv[0]
                df = DataFrame(dsv[1:], columns=cols, dtype=float)
            else:
                cols = [f"col{i+1}" for i in range(col_count)]
                df = DataFrame(dsv, columns=cols, dtype=float)
            return df
