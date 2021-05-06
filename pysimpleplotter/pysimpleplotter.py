#!/usr/bin/env python3

from enum import Enum
from typing import List, Dict, Any


from matplotlib.pyplot import Figure, Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pandas import DataFrame
from PySimpleGUI import (
    WIN_CLOSED,
    Canvas,
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
    popup_get_file,
)

from pysimpleplotter.guiconfig import GuiConfig
from pysimpleplotter.dataset import Dataset
from pysimpleplotter.exceptions import UnknownFileTypeError
from pysimpleplotter.plot import Plot

WindowKey = Enum(
    "WindowKey",
    [
        "CANVAS",
        "FILE_NAME",
        "FILE_TYPE",
        "FILE_NOT_FOUND",
        "COL",
        "COLS",
        "INVALID_PLOT_CONFIG",
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
        "SAVE_PLOT",
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
                Column(
                    [
                        *self.dataset_layout(),
                        *self.plot_layout(),
                    ],
                    vertical_alignment=align,
                ),
                Column(
                    [
                        [Canvas(size=(640, 480), key=WindowKey.CANVAS)],
                        [Button("Save", key=EventKey.SAVE_PLOT)],
                        # TODO: Add visual indication that the plot was saved
                    ],
                ),
            ],
            [Button("Exit")],
        ]
        window = Window(self.gui_config.window_title, layout)
        return window

    def dataset_layout(self) -> Layout:
        file_name_text_size = (9, 1)
        file_name_text_size = (9, 1)
        button_size = (6, 1)
        return [
            [Text("Input dataset", font=self.gui_config.title_font)],
            [
                Text("File name", font=self.gui_config.body_font),
                Input(key=WindowKey.FILE_NAME),
                FilesBrowse(size=button_size),
            ],
            [
                Text(
                    "",
                    size=(43, 1),
                    pad=((5, 17), (0, 0)),
                    key=WindowKey.FILE_NOT_FOUND,
                    font=self.gui_config.body_font,
                    text_color="orange",
                ),
                Button("Load", key=EventKey.LOAD, size=button_size),
            ],
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
            [
                Button("Plot", key=EventKey.PLOT),
                Text(
                    "",
                    size=(47, 1),
                    key=WindowKey.INVALID_PLOT_CONFIG,
                    font=self.gui_config.body_font,
                    text_color="orange",
                ),
            ],
        ]

    def handle(self, window: Window, event: EventKey, values: Dict[Any, Any]) -> None:
        try:
            if event == EventKey.LOAD:
                self.load(window, event, values)
            elif event == EventKey.RENAME_COL:
                self.rename_col(window, event, values)
            elif event == EventKey.PLOT:
                self.plot(window, event, values)
            elif event == EventKey.SAVE_PLOT:
                self.save_plot()
        except FileNotFoundError as e:
            self.file_not_found(window, True)
        except KeyError as e:
            self.invalid_plot_config(window, True)

    def load(self, window: Window, event: EventKey, values: Dict[Any, Any]) -> None:
        self.file_not_found(window, False)
        dataset = Dataset(
            file_name=values[WindowKey.FILE_NAME],
        )
        self.dfs.insert(0, dataset.load())
        window[WindowKey.COLS].update(self.dfs[0].columns)
        if len(self.dfs[0].columns) >= 2:
            window[WindowKey.TITLE].update(
                f"{self.dfs[0].columns[1]} vs. {self.dfs[0].columns[0]}"
            )
            window[WindowKey.X_COL].update(self.dfs[0].columns[0])
            window[WindowKey.Y_COL].update(self.dfs[0].columns[1])
        # TODO: Add a debug mode to print things like the below
        # print(self.dfs[0])

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
        if values[WindowKey.X_COL] and values[WindowKey.Y_COL]:
            self.invalid_plot_config(window, False)
            plot = Plot(
                title=values[WindowKey.TITLE],
                x_col=values[WindowKey.X_COL],
                y_col=values[WindowKey.Y_COL],
            )
            self.fig, self.ax = plot.plot(self.dfs[0])
            fig_agg = FigureCanvasTkAgg(self.fig, window[WindowKey.CANVAS].TKCanvas)
            fig_agg.get_tk_widget().pack()
            fig_agg.draw()
        else:
            self.invalid_plot_config(window, True)

    def save_plot(self) -> None:
        file_name = popup_get_file("Choose where to save your plot")
        if file_name:
            self.fig.savefig(file_name)

    def file_not_found(self, window, display: bool):
        if display:
            window[WindowKey.FILE_NOT_FOUND].update("File not found")
        else:
            window[WindowKey.FILE_NOT_FOUND].update("")

    def invalid_plot_config(self, window, display: bool):
        if display:
            window[WindowKey.INVALID_PLOT_CONFIG].update("Invalid plot configuration")
        else:
            window[WindowKey.INVALID_PLOT_CONFIG].update("")


if __name__ == "__main__":
    PySimplePlotter().gui()
