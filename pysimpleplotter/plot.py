#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Tuple

# import matplotlib.pyplot as plt
from matplotlib.pyplot import subplots, Figure, Axes
from pandas import DataFrame


@dataclass(frozen=True)
class Plot:
    title: str
    x_col: str
    y_col: str

    def plot(self, df: DataFrame) -> Tuple[Figure, Axes]:
        fig, ax = subplots()
        ax.set_title(self.title)
        ax.set_xlabel(self.x_col)
        ax.set_ylabel(self.y_col)
        ax.plot(df[self.x_col], df[self.y_col])
        return fig, ax
