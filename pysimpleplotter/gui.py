#!/usr/bin/env python3
import matplotlib.pyplot as plt
import pandas as pd
import PySimpleGUI as sg

from dataset import Dataset


def main():
    config = {
        "dataset": {
            "file_name": "ob-Phthalocyannine.txt",
            "file_type": "perkin_elmer",
            "cols": [
                "time",
                "weight",
                "baseline_weight",
                "program_temperature",
                "temperature",
                "gas_flow",
            ],
        },
        "plot": {
            "title": "Weight vs. Temperature",
            "x": "temperature",
            "y": "weight",
        },
    }
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
            config["dataset"].update({"cols": cols})
        if event == "-TITLE_IN-":
            config["plot"].update({"title": values["-TITLE_IN-"]})
        if event == "-X_IN-":
            config["plot"].update({"x": values["-X_IN-"]})
        if event == "-Y_IN-":
            config["plot"].update({"y": values["-Y_IN-"]})
        if event == "-PLOT-":
            dataset = Dataset(**config["dataset"])
            df = dataset.load()
            plot(df, **config["plot"])
        print(event, config)
    window.close()


def input_dataset_layout():
    return [
        [sg.Text("Input dataset", font="Bold 15")],
        [
            sg.Text("File name", pad=((32, 0), (0, 0)), font="Any 11"),
            sg.Input(key="-FILE_NAME_IN-", enable_events=True),
            sg.FilesBrowse(),
        ],
        [
            sg.Text("Type", pad=((32, 0), (0, 0)), font="Any 11"),
            sg.InputCombo(
                ("TSV", "Perkin Elmer"),
                default_value="TSV",
                key="-FILE_TYPE_IN-",
                enable_events=True,
            ),
        ],
        [
            sg.Text("Column names", pad=((32, 0), (0, 0)), font="Any 11"),
            sg.Input(key="-COL_IN-"),
            sg.Button("Add", key="-ADD_COL-"),
        ],
        [
            sg.Listbox(
                values=[],
                pad=((64, 0), (0, 0)),
                size=(16, 8),
                key="-COLS-",
            ),
        ],
    ]


def plot_config_layout():
    return [
        [sg.Text("Plot Configuration", font="Bold 15")],
        [
            sg.Text("Title", pad=((32, 0), (0, 0)), font="Any 11"),
            sg.Input(key="-TITLE_IN-", enable_events=True),
        ],
        [
            sg.Text("x-axis Column", pad=((32, 0), (0, 0)), font="Any 11"),
            sg.Input(key="-X_IN-", enable_events=True),
        ],
        [
            sg.Text("y-axis Column", pad=((32, 0), (0, 0)), font="Any 11"),
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
