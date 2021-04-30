#!/usr/bin/env python3

import matplotlib.pyplot as plt

from dataclasses import dataclass


@dataclass(frozen=True)
class Plot:
    title: str
    x_col: str
    y_col: str

    def plot(self, df) -> None:
        fig, ax = plt.subplots()
        ax.set_title(self.title)
        ax.set_xlabel(self.x_col)
        ax.set_ylabel(self.y_col)
        ax.plot(df[self.x_col], df[self.y_col])
        plt.show()
