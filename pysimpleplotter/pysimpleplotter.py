#!/usr/bin/env python3

from enum import Enum
from typing import List, Dict, Any

from matplotlib.pyplot import Figure
from pandas import DataFrame
from PySimpleGUI import (
    WIN_CLOSED,
    Column,
    Element,
    Frame,
    Button,
    Window,
    Text,
    Input,
    Combo,
    FilesBrowse,
    Listbox,
)

from pysimpleplotter.guiconfig import GuiConfig
from pysimpleplotter.dataset import Dataset
from pysimpleplotter.plot import Plot

WindowKey = Enum(
    "WindowKey",
    [
        "FILE_NAME",
        "FILE_TYPE",
        "COL",
        "COLS",
        "TITLE",
        "X_COL",
        "Y_COL",
    ],
)

EventKey = Enum(
    "EventKey",
    [
        "RENAME_COL",
        "LOAD",
        "PLOT",
    ],
)

Layout = List[List[Element]]


class PySimplePlotter:
    """Plots simple delimited data.

    gui_config: GuiConfig
    dfs: List[DataFrame]
    plts: List[Figure]
    configs: List[[Dict[str, Any]]

    Where input_configs holds JSON configurations for dfs & plts in the following schema:
    {
        "df": {
            "file_name": str,
            "cols": List[str]
        }
        "plt": {
            "title": str,
            "x": str,
            "y": str,
        }
    }

    Examples:
        PySimplePlotter().gui()
    """

    def __init__(
        self,
        gui_conifg: GuiConfig = None,
        dfs: List[DataFrame] = None,
        plts: List[Figure] = None,
        input_configs: List[Dict[str, Any]] = None,
    ):
        self.gui_config = GuiConfig(
            window_title="PySimplePlotter",
            title_font=("Any", 15, "bold"),
            body_font=("Any", 11),
        )
        self.dfs = []
        self.plts = []
        self.input_configs = []

    def gui(self) -> None:
        window = self.window()
        while True:
            event, values = window.read()
            if event == WIN_CLOSED or event == "Exit":
                break
            self.handle(window, event, values)
        window.close()

    def window(self) -> Window:
        align = "top"
        layout = [
            [
                Column(self.dataset_layout(), vertical_alignment=align),
                Column(self.plot_layout(), vertical_alignment=align),
            ],
            [Button("Exit")],
        ]
        window = Window(self.gui_config.window_title, layout)
        return window

    def dataset_layout(self) -> Layout:
        return [
            [Text("Input dataset", font=self.gui_config.title_font)],
            [
                Text("File name", font=self.gui_config.body_font),
                Input(key=WindowKey.FILE_NAME, enable_events=True),
                FilesBrowse(),
            ],
            [Button("Load", key=EventKey.LOAD)],
            [self.columns_frame()],
        ]

    def columns_frame(self) -> Element:
        return Frame(
            "Columns",
            [
                [Text("Select a column to rename it", font=self.gui_config.body_font)],
                [
                    Listbox(
                        values=[],
                        size=(45, 4),
                        key=WindowKey.COLS,
                    ),
                ],
                [
                    Input(key=WindowKey.COL),
                    Button(
                        "Rename",
                        key=EventKey.RENAME_COL,
                    ),
                ],
            ],
            font=self.gui_config.body_font,
        )

    def plot_layout(self) -> Layout:
        return [
            [Text("Plot configuration", font=self.gui_config.title_font)],
            [
                Text("Title", font=self.gui_config.body_font),
                Input(key=WindowKey.TITLE),
            ],
            [
                Text("x-axis Column", font=self.gui_config.body_font),
                Input(key=WindowKey.X_COL),
            ],
            [
                Text("y-axis Column", font=self.gui_config.body_font),
                Input(key=WindowKey.Y_COL),
            ],
            # TODO: Include the plot in-window
            [Button("Plot", key=EventKey.PLOT)],
        ]

    def handle(self, window: Window, event: EventKey, values: Dict[Any, Any]) -> None:
        # TODO: Add load visualization
        if event == EventKey.LOAD:
            self.load(window, event, values)
        elif event == EventKey.RENAME_COL:
            self.rename_col(window, event, values)
        # TODO: Add error handling
        elif event == EventKey.PLOT:
            self.plot(window, event, values)

    def load(self, window: Window, event: EventKey, values: Dict[Any, Any]) -> None:
        dataset = Dataset(
            file_name=values[WindowKey.FILE_NAME],
        )
        self.dfs.insert(0, dataset.load())
        window[WindowKey.COLS].update(self.dfs[0].columns)
        window[WindowKey.TITLE].update(
            f"{self.dfs[0].columns[1]} vs. {self.dfs[0].columns[0]}"
        )
        window[WindowKey.X_COL].update(self.dfs[0].columns[0])
        window[WindowKey.Y_COL].update(self.dfs[0].columns[1])
        print(self.dfs[0])

    def rename_col(
        self, window: Window, event: EventKey, values: Dict[Any, Any]
    ) -> None:
        cols = window[WindowKey.COLS].get_list_values()
        index = window[WindowKey.COLS].get_indexes()[0]
        cols[index] = values[WindowKey.COL]
        self.dfs[0].columns = cols
        window[WindowKey.COLS].update(cols)
        window[WindowKey.COL].update("")
        print(self.dfs[0])

    def plot(self, window: Window, event: EventKey, values: Dict[Any, Any]) -> None:
        plot = Plot(
            title=values[WindowKey.TITLE],
            x_col=values[WindowKey.X_COL],
            y_col=values[WindowKey.Y_COL],
        )
        plot.plot(self.dfs[0])


if __name__ == "__main__":
    PySimplePlotter().gui()
