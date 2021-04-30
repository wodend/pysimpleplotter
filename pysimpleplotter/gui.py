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

from config import Config
from dataset import Dataset
from plot import Plot

from numpy import float64

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


def main() -> None:
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


def dataset_layout(config: Config) -> Layout:
    return [
        [Text("Input dataset", font=config.title_font)],
        [
            Text("File name", font=config.body_font),
            Input(key=WindowKey.FILE_NAME, enable_events=True),
            FilesBrowse(),
        ],
        [Button("Load", key=EventKey.LOAD)],
        [columns_frame(config)],
    ]


def columns_frame(config: Config) -> Element:
    return Frame(
        "Columns",
        [
            # [Text("Select a column to rename it", font=config.body_font)],
            [
                Listbox(
                    values=[],
                    size=(45, 4),
                    key=WindowKey.COLS,
                ),
            ],
            # TODO: Add rename column feature
            # [
            #     Input(key=WindowKey.COL),
            #     Button(
            #         "Rename",
            #         key=EventKey.RENAME_COL,
            #     ),
            # ],
        ],
        font=config.body_font,
    )


def plot_layout(config: Config) -> Layout:
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


def handle(window: Window, event: EventKey, values: Dict[Any, Any]):
    # TODO: Refactor to group events acting on columns and on DataFrames
    if event == EventKey.RENAME_COL:
        cols = window[WindowKey.COLS].get_list_values()
        index = window[WindowKey.COLS].get_indexes()[0]
        cols[index] = values[WindowKey.COL]
        window[WindowKey.COLS].update(cols)
    # TODO: Add load visualization
    elif event == EventKey.LOAD:
        dataset = Dataset(
            file_name=values[WindowKey.FILE_NAME],
        )
        df = dataset.load()
        window[WindowKey.COLS].update(df.columns)
        window[WindowKey.TITLE].update(f"{df.columns[1]} vs. {df.columns[0]}")
        window[WindowKey.X_COL].update(df.columns[0])
        window[WindowKey.Y_COL].update(df.columns[1])
        print(df)
    # TODO: Add error handling
    elif event == EventKey.PLOT:
        dataset = Dataset(
            file_name=values[WindowKey.FILE_NAME],
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
