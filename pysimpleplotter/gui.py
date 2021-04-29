#!/usr/bin/env python3

from dataclasses import dataclass
from enum import Enum, IntEnum
from json import (
    JSONEncoder,
    load as load_json,
    dump as dump_json,
)
from typing import List, Dict, Any

from PySimpleGUI import (
    LISTBOX_SELECT_MODE_EXTENDED,
    WIN_CLOSED,
    Column,
    Frame,
    Button,
    Window,
    Text,
    Input,
    Combo,
    FilesBrowse,
    Listbox,
)

from config import Config
from dataset import Dataset
from plot import Plot

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
        "ADD_COL",
        "DEL_COLS",
        "LOAD",
        "PLOT",
    ],
)


def main():
    config = Config(
        window_title="PySimplePlotter",
        title_font=("Any", 15, "bold"),
        body_font=("Any", 11),
    )
    layout = [
        [
            Column(dataset_layout(config), vertical_alignment="top"),
            Column(plot_layout(config), vertical_alignment="top"),
        ],
        [Button("Exit")],
    ]
    window = Window(config.window_title, layout)
    while True:
        event, values = window.read()
        if event == WIN_CLOSED or event == "Exit":
            break
        handle(window, event, values)
    window.close()


def dataset_layout(config):
    return [
        [Text("Input dataset", font=config.title_font)],
        [
            Text("File name", font=config.body_font),
            Input(key=WindowKey.FILE_NAME),
            FilesBrowse(),
        ],
        [
            Text("File Type", font=config.body_font),
            Combo(
                # TODO: Decouple representation from logic, probably add to dataset.py
                ("TSV", "Perkin Elmer"),
                default_value="TSV",
                key=WindowKey.FILE_TYPE,
            ),
        ],
        [columns_layout(config)],
        [Button("Load", key=EventKey.LOAD)],
    ]


def columns_layout(config):
    return Frame(
        "Columns",
        [
            [
                Input(key=WindowKey.COL),
                Button("Add", key=EventKey.ADD_COL),
            ],
            [
                Listbox(
                    select_mode=LISTBOX_SELECT_MODE_EXTENDED,
                    values=[],
                    size=(45, 4),
                    key=WindowKey.COLS,
                    enable_events=True,
                ),
            ],
            [
                Button(
                    "Remove selected column(s)",
                    key=EventKey.DEL_COLS,
                ),
            ],
        ],
        font=config.body_font,
    )


def plot_layout(config):
    return [
        [Text("Plot Configuration", font=config.title_font)],
        [
            Text("Title", font=config.body_font),
            Input(key=WindowKey.TITLE),
        ],
        [
            Text("x-axis Column", font=config.body_font),
            Input(key=WindowKey.X_COL),
        ],
        [
            Text("y-axis Column", font=config.body_font),
            Input(key=WindowKey.Y_COL),
        ],
        # TODO: Include the plot in-window
        [Button("Plot", key=EventKey.PLOT)],
    ]


def handle(window, event, values):
    # TODO: Refactor to group events acting on columns and on DataFrames
    if event == EventKey.ADD_COL:
        cols = window[WindowKey.COLS].get_list_values()
        window[WindowKey.COLS].update(cols + [values[WindowKey.COL]])
        window[WindowKey.COL].update("")
    elif event == EventKey.DEL_COLS:
        cols = window[WindowKey.COLS].get_list_values()
        for i in reversed(sorted(window[WindowKey.COLS].get_indexes())):
            del cols[i]
        window[WindowKey.COLS].update(cols)
    # TODO: Add load visualization
    elif event == EventKey.LOAD:
        pass
    # TODO: Add error handling
    elif event == EventKey.PLOT:
        dataset = Dataset(
            file_name=values[WindowKey.FILE_NAME],
            file_type=values[WindowKey.FILE_TYPE],
            cols=window[WindowKey.COLS].get_list_values(),
        )
        df = dataset.load()
        plot = Plot(
            title=values[WindowKey.TITLE],
            x_col=values[WindowKey.X_COL],
            y_col=values[WindowKey.Y_COL],
        )
        plot.plot(df)


if __name__ == "__main__":
    main()
