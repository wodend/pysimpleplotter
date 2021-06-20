#!/usr/bin/env python3

from dataclasses import dataclass

@dataclass(frozen=True)
class Relation:
    name: str
    independent_dataset: str
    independent_col: str
    dependent_dataset: str
    dependent_col: str
    color: str
