#!/usr/bin/env python3

import dataclasses
from enum import Enum
from os.path import split, splitext, getsize
from typing import List, Dict, Any

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pandas import DataFrame
from PySimpleGUI import (
    DEFAULT_ELEMENT_SIZE,
    WIN_CLOSED,
    RELIEF_SUNKEN,
    Canvas,
    Column,
    ColorChooserButton,
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
from pysimpleplotter.relation import Relation


Layout = List[List[Element]]


def human_readable(byte_count: int, _format: str = "{value:.3f} {symbol}") -> str:
    symbols = ("B", "K", "M", "G", "T", "P", "E", "Z", "Y")
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i + 1) * 10
    for symbol in reversed(symbols[1:]):
        if byte_count >= prefix[symbol]:
            value = float(byte_count) / prefix[symbol]
            return _format.format(**locals())
    return _format.format(value=byte_count, symbol=symbols[0])


class PySimplePlotter:
    """Plots simple delimited data.

    Examples:
        PySimplePlotter().gui()

    Attributes:
        gui_config: A GuiConfig defining how the window should look
        datasets: A dict of names mapped to Datasets defining the files for dfs
        dfs: A dict of names mapped of DataFrames for the plotting data
        relations: A dict of names mapped to variable relations to plot
        window: A Window which displays and stores user input
    """

    def __init__(self):
        self.gui_config = GuiConfig(
            window_title="PySimplePlotter",
            title_font=("Any", 15, "bold"),
            body_font=("Any", 11),
            valign="top",
            frame_size=(64, 1),
        )
        self.datasets: Dict[str, Dataset] = {}
        self.dfs: Dict[str, DataFrame] = {}
        self.relations: Dict[str, Relation] = {}
        self.window: Window = None
        self.fig: Figure = None
        self.ax: Axes = None

    def gui(self) -> None:
        self.initialize_window()
        while True:
            event, values = self.window.read()
            if event == WIN_CLOSED or event == "Exit":
                break
            self.handle(event, values)
        self.window.close()

    def initialize_window(self) -> None:
        layout = [
            [
                Frame(
                    "Datasets",
                    self.datasets_layout(),
                    vertical_alignment=self.gui_config.valign,
                    size=self.gui_config.frame_size,
                ),
                Frame(
                    "Columns",
                    self.columns_layout(),
                    vertical_alignment=self.gui_config.valign,
                ),
                Frame(
                    "Relationships",
                    self.relations_layout(),
                    vertical_alignment=self.gui_config.valign,
                ),
            ],
            [
                Frame(
                    "Plot",
                    self.plot_layout(),
                    vertical_alignment=self.gui_config.valign,
                ),
                Column(
                    self.canvas_layout(),
                    vertical_alignment=self.gui_config.valign,
                ),
            ],
        ]
        self.window = Window(self.gui_config.window_title, layout)

    def datasets_layout(self) -> Layout:
        return [
            *self.selector(
                controls=[
                    Input(
                        "",
                        size=(0, 0),
                        enable_events=True,
                        key="-OPEN_DATASET-",
                        visible=False,
                    ),
                    FilesBrowse(
                        "Open",
                        file_types=(
                            ("Delimiter-separated values", "*.csv *.tsv *.txt"),
                            ("All files", "*"),
                        ),
                    ),
                    Button("Remove", key="-REMOVE_DATASET-"),
                ],
                select_key="-SELECT_DATASET-",
                rename_key="-RENAME_DATASET-",
                default_text="No datasets",
            ),
            *self.display(
                [
                    "File name:",
                    "File size:",
                    "Number of rows:",
                    "Number of columns:",
                ],
                [
                    "-FILE_NAME-",
                    "-FILE_SIZE-",
                    "-ROW_COUNT-",
                    "-COL_COUNT-",
                ],
            ),
        ]

    def columns_layout(self) -> Layout:
        return [
            *self.selector(
                controls=[
                    Button("New", key="-NEW_COL-"),
                    Button("Remove", key="-REMOVE_COL-"),
                ],
                select_key="-SELECT_COL-",
                rename_key="-RENAME_COL-",
                default_text="No columns",
            ),
            *self.display(
                [
                    "Mean:",
                    "Median:",
                    "Minimum:",
                    "Maximum:",
                ],
                [
                    "-MEAN-",
                    "-MEDIAN-",
                    "-MIN-",
                    "-MAX-",
                ],
            ),
        ]

    def display(self, text: List[str], keys: List[str]):
        return (
            [
                Column(
                    [
                        [Text(text, size=(17, 1), justification="right")]
                        for text in text
                    ],
                    pad=(0, 0),
                ),
                Column(
                    [[self.display_field(key)] for key in keys],
                    pad=(0, 0),
                ),
            ],
        )

    def display_field(self, key: str, default_text: str = "None") -> Text:
        return Text(
            default_text,
            text_color="dark grey",
            key=key,
            justification="right",
            metadata={"initialized": False},
            size=(27, 1),
        )

    def dropdown(self, key: str, width: int = 45) -> Combo:
        return Combo(
            [],
            enable_events=True,
            key=key,
            metadata={"initialized": False},
            disabled=True,
            size=(width, 1),
        )

    def relations_layout(self) -> Layout:
        return [
            *self.selector(
                controls=[
                    Button("New", key="-NEW_RELATION-"),
                    Button("Remove", key="-REMOVE_RELATION-"),
                ],
                select_key="-SELECT_RELATION-",
                rename_key="-RENAME_RELATION-",
                default_text="No relationships",
            ),
            [
                Column(
                    [
                        [Text("Variable")],
                        [Text("Independent")],
                        [Text("Dependent")],
                    ],
                    pad=(0, 0),
                ),
                Column(
                    [
                        [Text("Dataset")],
                        [self.dropdown("-SELECT_INDEPENDENT_DATASET-", 15)],
                        [self.dropdown("-SELECT_DEPENDENT_DATASET-", 15)],
                    ],
                    pad=(0, 0),
                ),
                Column(
                    [
                        [Text("Column")],
                        [self.dropdown("-SELECT_INDEPENDENT_COL-", 12)],
                        [self.dropdown("-SELECT_DEPENDENT_COL-", 12)],
                    ],
                    pad=(0, 0),
                ),
            ],
            [
                Text("Color"),
                Text("", key="-COLOR-", pad=((10, 0), (0, 0)), size=(20, 1), relief=RELIEF_SUNKEN),
                Input("", key="-SELECT_COLOR-", size=(1, 1), visible=False, enable_events=True),
                ColorChooserButton("Choose"),
            ],
        ]

    def selector(
        self,
        controls: List[Element],
        select_key: str,
        rename_key: str,
        default_text: str,
    ) -> Layout:
        return [
            controls,
            [
                Listbox(
                    [default_text],
                    enable_events=True,
                    size=(45, 4),
                    key=select_key,
                    disabled=True,
                    metadata={
                        "initialized": False,
                    },
                ),
            ],
            [
                Input(
                    enable_events=True,
                    key=rename_key,
                    text_color="dark grey",
                    disabled=True,
                    metadata={
                        "initialized": False,
                    },
                ),
            ],
        ]

    def plot_layout(self) -> Layout:
        return [
            [Text("Title")],
            [
                Input(key="-PLOT_TITLE-"),
            ],
            [
                Column(
                    [
                        [Text("Axis")],
                        [Text("X")],
                        [Text("Y")],
                    ],
                    pad=(0, 0),
                ),
                Column(
                    [
                        [Text("Label")],
                        [Input(key="-X_AXIS_LABEL-", size=(25, 1))],
                        [Input(key="-Y_AXIS_LABEL-", size=(25, 1))],
                    ],
                    pad=(0, 0),
                ),
                Column(
                    [
                        [Text("Units")],
                        [Input(key="-X_AXIS_UNITS-", size=(12, 1))],
                        [Input(key="-Y_AXIS_UNITS-", size=(12, 1))],
                    ],
                    pad=(0, 0),
                ),
            ],
            [
                Column(
                    [
                        [Text("Style")],
                        [
                            Combo(
                                [
                                    "Default",
                                ],
                                default_value="Default",
                                key="-STYLE-",
                            )
                        ],
                    ],
                    pad=(0, 0),
                ),
                Column(
                    [
                        [Text("Type")],
                        [Combo(["Line", "Bar"], default_value="Line", key="-TYPE-")],
                    ],
                    pad=(0, 0),
                ),
            ],
            [
                Button("Plot", key="-PLOT-"),
            ],
        ]

    def canvas_layout(self) -> Layout:
        return [
            [Canvas(size=(640, 480), key="-CANVAS-")],
            [
                Button("Save", key="-SAVE_PLOT-"),
            ],
        ]

    def handle(self, event: str, values: Dict[Any, Any]) -> None:
        try:
            print("###################################################")
            print(event, values)

            # Datasets
            if event == "-OPEN_DATASET-":
                self.open_dataset(values)
            if event == "-SELECT_DATASET-":
                self.select_dataset(values["-SELECT_DATASET-"][0])
            if event == "-RENAME_DATASET-":
                self.rename_dataset(values)

            # Columns
            if event == "-SELECT_COL-":
                self.select_col(
                    values["-SELECT_DATASET-"][0],
                    values["-SELECT_COL-"][0],
                )
            if event == "-RENAME_COL-":
                self.rename_col(values)

            # Relationships
            if event == "-NEW_RELATION-":
                self.new_relation(values)
            if event == "-SELECT_RELATION-":
                self.select_relation(values["-SELECT_RELATION-"][0])
            if event == "-RENAME_RELATION-":
                self.rename_relation(values)
            if event == "-SELECT_INDEPENDENT_DATASET-":
                self.select_independent_dataset(values)
            if event == "-SELECT_DEPENDENT_DATASET-":
                self.select_dependent_dataset(values)
            if event == "-SELECT_INDEPENDENT_COL-":
                self.select_independent_col(values)
            if event == "-SELECT_DEPENDENT_COL-":
                self.select_dependent_col(values)
            if event == "-SELECT_COLOR-":
                self.select_color(values)
            if event == "-PLOT-":
                self.plot(values)
        except Exception as e:
            # print(e)
            raise e

    def open_dataset(self, values: Dict[Any, Any]) -> None:
        raw_file_names = values["-OPEN_DATASET-"]
        file_names = raw_file_names.split(";")
        for index, file_name in enumerate(file_names):
            name = splitext(split(file_name)[1])[0]
            self.datasets[name] = Dataset(name, file_name)
            self.dfs[name] = self.datasets[name].load()
            added_index = self.add_list("-SELECT_DATASET-", name)
            if index == 0:
                first_index = added_index
                first_name = name
        self.window["-SELECT_DATASET-"].update(set_to_index=first_index)
        self.select_dataset(name)
        self.window["-SELECT_INDEPENDENT_DATASET-"].update(
            values=self.window["-SELECT_DATASET-"].get_list_values(),
        )
        self.window["-SELECT_DEPENDENT_DATASET-"].update(
            values=self.window["-SELECT_DATASET-"].get_list_values(),
        )

    def add_list(self, key: str, item: str) -> int:
        if not self.window[key].metadata["initialized"]:
            self.set_list(key, [])
            self.window[key].metadata["initialized"] = True
        items = self.window[key].get_list_values()
        index = len(items)
        items.append(item)
        self.set_list(key, items, index)
        return index

    def display_input(self, element_key: str, text: str) -> None:
        if not self.window[element_key].metadata["initialized"]:
            if hasattr(self.window[element_key], "Disabled"):
                self.window[element_key].update("", disabled=False)
            else:
                self.window[element_key].update("")
            self.window[element_key].metadata["initialized"] = True
        self.window[element_key].update(text, text_color="black")
        self.window[element_key].set_tooltip(text)
        self.window[element_key].set_focus()

    def display_text(self, element_key: str, text: str):
        self.window[element_key].update(text, text_color="white")
        self.window[element_key].set_tooltip(text)

    def set_list(self, list_key: str, values: List, index: int = 0) -> None:
        self.window[list_key].update(values, disabled=False, set_to_index=index)

    def select_dataset(self, name: str) -> None:
        # Update dataset layout
        self.display_input("-RENAME_DATASET-", name)
        self.display_text("-FILE_NAME-", self.datasets[name].file_name)
        self.display_text(
            "-FILE_SIZE-",
            human_readable(getsize(self.datasets[name].file_name)),
        )
        self.display_text("-ROW_COUNT-", len(self.dfs[name].index))
        self.display_text("-COL_COUNT-", len(self.dfs[name].columns))

        # Update column layout
        self.set_list("-SELECT_COL-", self.dfs[name].columns)
        self.select_col(name, self.dfs[name].columns[0])

    def rename_dataset(self, values: Dict[Any, Any]) -> None:
        old_name = values["-SELECT_DATASET-"][0]
        new_name = values["-RENAME_DATASET-"]
        self.datasets[new_name] = dataclasses.replace(
            self.datasets.pop(old_name),
            name=new_name,
        )
        self.dfs[new_name] = self.dfs.pop(old_name)
        self.rename_selected("-SELECT_DATASET-", new_name)

    def select_col(self, dataset: str, name: str) -> None:
        # TODO: Add error handling
        self.display_input("-RENAME_COL-", name)
        f = "{0:,.3f}"
        self.display_text("-MEAN-", f.format(self.dfs[dataset][name].mean()))
        self.display_text("-MEDIAN-", f.format(self.dfs[dataset][name].median()))
        self.display_text("-MIN-", f.format(self.dfs[dataset][name].min()))
        self.display_text("-MAX-", f.format(self.dfs[dataset][name].max()))

    def rename_col(self, values: Dict[Any, Any]) -> None:
        new_name = values["-RENAME_COL-"]
        self.rename_selected("-SELECT_COL-", new_name)
        dataset = values["-SELECT_DATASET-"][0]
        self.dfs[dataset].columns = self.window["-SELECT_COL-"].get_list_values()

    def rename_selected(self, select_key: str, name: str) -> None:
        index = self.window[select_key].get_indexes()[0]
        items = self.window[select_key].get_list_values()
        items[index] = name
        self.set_list(select_key, items, index)

    def new_relation(self, values: Dict[Any, Any]) -> None:
        items = self.window["-SELECT_RELATION-"].get_list_values()
        if not self.window["-SELECT_RELATION-"].metadata["initialized"]:
            index = 0
        else:
            index = len(items)
        name = f"relation{index+1}"

        # TODO: Display error if no datasets are loaded
        dataset = self.window["-SELECT_DATASET-"].get()[0]
        dataset_cols = list(self.dfs[dataset].columns)
        independent_dataset = dataset
        independent_col = dataset_cols[0]
        dependent_dataset = dataset
        dependent_col = dataset_cols[1]
        self.relations[name] = Relation(
            name,
            independent_dataset,
            independent_col,
            dependent_dataset,
            dependent_col,
            "#000000",
        )
        added_index = self.add_list("-SELECT_RELATION-", name)
        self.select_relation(name)

    def select_relation(self, name: str) -> None:
        # TODO: Add error handling
        relation = self.relations[name]
        self.display_input("-RENAME_RELATION-", name)

        datasets = self.window["-SELECT_DATASET-"].get_list_values()
        # TODO: Add error handling if selected datasets are removed
        independent_dataset_index = datasets.index(relation.independent_dataset)
        dependent_dataset_index = datasets.index(relation.dependent_dataset)
        independent_dataset_cols = list(self.dfs[datasets[independent_dataset_index]].columns)
        dependent_dataset_cols = list(self.dfs[datasets[dependent_dataset_index]].columns)
        # TODO: Add error handling if selected cols are removed
        independent_col_index = independent_dataset_cols.index(relation.independent_col)
        dependent_col_index = dependent_dataset_cols.index(relation.dependent_col)
        self.window["-SELECT_INDEPENDENT_DATASET-"].update(
            values=datasets,
            disabled=False,
            set_to_index=independent_dataset_index,
        )
        self.window["-SELECT_DEPENDENT_DATASET-"].update(
            values=datasets,
            disabled=False,
            set_to_index=dependent_dataset_index,
        )
        self.window["-SELECT_INDEPENDENT_COL-"].update(
            values=independent_dataset_cols,
            disabled=False,
            set_to_index=independent_col_index,
        )
        self.window["-SELECT_DEPENDENT_COL-"].update(
            values=dependent_dataset_cols,
            disabled=False,
            set_to_index=dependent_col_index,
        )
        self.window["-COLOR-"].update(
            background_color=relation.color,
        )
        print(self.relations)

    def rename_relation(self, values: Dict[Any, Any]) -> None:
        old_name = values["-SELECT_RELATION-"][0]
        new_name = values["-RENAME_RELATION-"]
        self.relations[new_name] = dataclasses.replace(
            self.relations.pop(old_name),
            name=new_name,
        )
        self.rename_selected("-SELECT_RELATION-", new_name)

    def select_independent_dataset(self, values: Dict[Any, Any]) -> None:
        name = values["-SELECT_RELATION-"][0]
        new_independent_dataset = values["-SELECT_INDEPENDENT_DATASET-"]
        self.relations[name] = dataclasses.replace(
            self.relations[name],
            independent_dataset=new_independent_dataset,
        )
        self.window["-SELECT_INDEPENDENT_COL-"].update(
            values=list(self.dfs[new_independent_dataset].columns),
            set_to_index=0,
        )

    def select_dependent_dataset(self, values: Dict[Any, Any]) -> None:
        name = values["-SELECT_RELATION-"][0]
        new_dependent_dataset = values["-SELECT_DEPENDENT_DATASET-"]
        self.relations[name] = dataclasses.replace(
            self.relations[name],
            dependent_dataset=new_dependent_dataset,
        )
        self.window["-SELECT_DEPENDENT_COL-"].update(
            values=list(self.dfs[new_dependent_dataset].columns),
            set_to_index=0,
        )

    def select_independent_col(self, values: Dict[Any, Any]) -> None:
        name = values["-SELECT_RELATION-"][0]
        new_independent_col = values["-SELECT_INDEPENDENT_COL-"]
        self.relations[name] = dataclasses.replace(
            self.relations[name],
            independent_col=new_independent_col,
        )

    def select_dependent_col(self, values: Dict[Any, Any]) -> None:
        name = values["-SELECT_RELATION-"][0]
        new_dependent_col = values["-SELECT_DEPENDENT_COL-"]
        self.relations[name] = dataclasses.replace(
            self.relations[name],
            dependent_col=new_dependent_col,
        )

    # TODO: Refactor selection functions into one which takes the field as an argument
    def select_color(self, values: Dict[Any, Any]) -> None:
        name = values["-SELECT_RELATION-"][0]
        new_color = values["-SELECT_COLOR-"]
        print(f"Selecting color {new_color}")
        self.window["-COLOR-"].update(
            background_color=new_color,
        )
        self.relations[name] = dataclasses.replace(
            self.relations[name],
            color=new_color,
        )

    def plot(self, values: Dict[Any, Any]) -> None:
        # TODO: Add error handling
        if values["-STYLE-"] == "Default":
            style = {
                "axes.edgecolor": "black",
                "axes.facecolor": "white",
                "axes.labelcolor": "black",
                "axes.prop_cycle": plt.cycler(
                    "color", ["0.00", "0.40", "0.60", "0.70"]
                ),
                "figure.edgecolor": "white",
                "figure.facecolor": "0.75",
                "grid.color": "black",
                "image.cmap": "gray",
                "lines.color": "black",
                "patch.edgecolor": "black",
                "patch.facecolor": "gray",
                "savefig.edgecolor": "white",
                "savefig.facecolor": "white",
                "text.color": "black",
                "xtick.color": "black",
                "ytick.color": "black",
            }
        else:
            raise ValueError("No such style")
        # Create plot
        with plt.style.context(style):
            self.fig, self.ax = plt.subplots()
        for name, relation in self.relations.items():
            print(f"Plotting {name}: {relation}")
            x_df = self.dfs[relation.independent_dataset]
            x_col = relation.independent_col
            x_label = f"{values['-X_AXIS_LABEL-']}"
            if values["-X_AXIS_UNITS-"]:
                x_label += f" ({values['-X_AXIS_UNITS-']})"
            y_df = self.dfs[relation.dependent_dataset]
            y_col = relation.dependent_col
            y_label = f"{values['-Y_AXIS_LABEL-']}"
            if values["-Y_AXIS_UNITS-"]:
                y_label += f" ({values['-Y_AXIS_UNITS-']})"
            self.ax.set_title(values["-PLOT_TITLE-"])
            self.ax.set_xlabel(x_label)
            self.ax.set_ylabel(y_label)
            self.ax.plot(x_df[x_col], y_df[y_col], relation.color)

        # Display plot
        fig_agg = FigureCanvasTkAgg(self.fig, self.window["-CANVAS-"].TKCanvas)
        fig_agg.get_tk_widget().pack()
        fig_agg.draw()

    def save_plot(self) -> None:
        file_name = popup_get_file("Choose where to save your plot")
        if file_name:
            self.fig.savefig(file_name)


if __name__ == "__main__":
    PySimplePlotter().gui()
