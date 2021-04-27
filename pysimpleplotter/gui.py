#!/usr/bin/env python3
import matplotlib.pyplot as plt
import pandas as pd
import PySimpleGUI as sg

from dataset import Dataset


def main():
    config = config_template()
    title = "PySimplePlotter"
    layout = [
        *input_dataset_layout(),
        [sg.HorizontalSeparator()],
        *plot_config_layout(),
        [sg.Button("Plot", key="-PLOT-"), sg.Button("Exit")],
    ]
    window = sg.Window(title, layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        if event == "-FILE_NAME_IN-":
            config["dataset"].update({"file_name": values["-FILE_NAME_IN-"]})
        if event == "-FILE_TYPE_IN-":
            file_type = values["-FILE_TYPE_IN-"].lower().replace(" ", "_")
            config["dataset"].update({"file_type": file_type})
        if event == "-ADD_COL-":
            cols = window["-COLS-"].get_list_values() + [values["-COL_IN-"]]
            window["-COLS-"].update(values=cols)
            window["-COL_IN-"].update("")
            config["dataset"].update({"cols": cols})
        if event == "-TITLE_IN-":
            config["plot"].update({"title": values["-TITLE_IN-"]})
        if event == "-X_IN-":
            config["plot"].update({"x": values["-X_IN-"]})
        if event == "-Y_IN-":
            config["plot"].update({"y": values["-Y_IN-"]})
        if event == "-DEL_COL-":
            cols = window["-COLS-"].get_list_values()
            for i in window["-COLS-"].get_indexes():
                cols[i] = None
            cols_new = [x for x in cols if x is not None]
            window["-COLS-"].update(cols_new)
            config["dataset"].update({"cols": cols_new})
        if event == "-PLOT-":
            dataset = Dataset(**config["dataset"])
            df = dataset.load()
            plot(df, **config["plot"])
        print(event, config)
    window.close()


def config_template():
    return {
        "dataset": {
            "file_name": "",
            "file_type": "tsv",
            "cols": [],
        },
        "plot": {
            "title": "",
            "x": "",
            "y": "",
        },
    }

def input_dataset_layout():
    col_input_title = "Column names"
    return [
        [sg.Text("Input dataset", font=("Any", 15, "bold"))],
        [
            sg.Text("File name", font=("Any", 11)),
            sg.Input(key="-FILE_NAME_IN-", enable_events=True),
            sg.FilesBrowse(),
        ],
        [
            sg.Text("Type", font=("Any", 11)),
            sg.InputCombo(
                ("TSV", "Perkin Elmer"),
                default_value="TSV",
                key="-FILE_TYPE_IN-",
                enable_events=True,
            ),
        ],
        [
            sg.Text(col_input_title, font=("Any", 11)),
            sg.Input(key="-COL_IN-"),
            sg.Button("Add", key="-ADD_COL-"),
        ],
        [
            sg.Button(
                "Remove\nselected\ncolumn(s)",
                size=(len(col_input_title),0),
                key="-DEL_COL-",
            ),
            sg.Listbox(
                select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED,
                values=[],
                size=(45, 8),
                key="-COLS-",
                enable_events=True,
            ),
        ],
    ]


def plot_config_layout():
    return [
        [sg.Text("Plot Configuration", font=("Any", 15, "bold"))],
        [
            sg.Text("Title", font=("Any", 11)),
            sg.Input(key="-TITLE_IN-", enable_events=True),
        ],
        [
            sg.Text("x-axis Column", font=("Any", 11)),
            sg.Input(key="-X_IN-", enable_events=True),
        ],
        [
            sg.Text("y-axis Column", font=("Any", 11)),
            sg.Input(key="-Y_IN-", enable_events=True),
        ],
    ]


def plot(df, title, x, y):
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.plot(df[x], df[y])
    plt.show()


if __name__ == "__main__":
    main()
