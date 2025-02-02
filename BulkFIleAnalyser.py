"""
TODO
    * When file type is selected, update the window with selected type
    + Look at binding multiple functions so that updating the window does not need to be within the class definition
    * Modify get path function as a class to return list of files of set type within the chosen folder
    (See Test01.py)
        - Update window to show path
        - Update window to show number of files of type
    * Add validation to read of data file definitions
    * Create subclass of tkinter button class to return values of selected data folder and number of files cued
    --- Start of loop
        * Read in first file
        * Process data in first file
        * Add results of processing to results df
    --- End of loop
    * Write results df to file
    Known bugs
    ==========
"""
import glob
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askdirectory
# import pandas as pd
import numpy as np
import csv
import os
import sys
import fnmatch
# from tkinter import ttk
from tkinter import *

def temp_show_info(passed_info):
    print(f"Passed info: >>>{passed_info.import_settings}<<<")

def quit_script():
    print("Leaving program")
    main_window.destroy()
    exit()


def get_file_definitions():
    # Set file to default location and name
    data_def_file = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "DataFileSpec.txt") 
    if os.path.exists(data_def_file):  # If the default file exists
        arr = np.genfromtxt(
            data_def_file,
            comments='#',
            names=True,
            dtype=None
            # dtype=['<U17', '<U3', '<U2', '<i8', '<i8', '<i8', '<i8', '<U6', '<U19']
        )
        return arr
    else:
        messagebox.showerror(
            title="Failed to read data file definitions",
            message="Aborting: No data file definitions found",
            detail="Search path:\n" + data_def_file,
            icon='error'
        )
        return -1

class Get_filetype:
    def __init__(self, defined_filetypes):
        self.file_defs = defined_filetypes # Copy passed filetypes so they will be available for other class functions
        self.type_list = self.file_defs['source'].tolist()   # Strip out list of defined source types
        # create choose data file type label
        choose_data_filetype_frm = LabelFrame(main_window, text="Select data file type")
        choose_data_filetype_frm.pack(padx=pdx, pady=pdy, side=tk.LEFT )
        # create combobox object to select data file type
        self.defined_types = tk.StringVar()
        data_filetype_combo = ttk.Combobox(choose_data_filetype_frm, textvariable=self.defined_types, state='readonly')
        data_filetype_combo['values'] = self.type_list
        data_filetype_combo.bind('<<ComboboxSelected>>', self.get_import_file_defs)  # bind function for when value changed
        data_filetype_combo.pack(padx=pdx, pady=pdy)

    def get_import_file_defs(self, event):
        self.import_settings = self.file_defs[self.file_defs['source'] == event.widget.get()]


def data_filetype_selected(event):
    file_type_label_gridinfo = choose_data_filetype_lbl.grid_info()   # Get grid info of existing label
    # Remove selection combo and label
    choose_data_filetype_lbl.grid_remove()
    data_filetype_combo.grid_remove()
    # Grid the label frame
    # data_filetype_frm.grid(
        # row=file_type_label_gridinfo['row'],
        # column=file_type_label_gridinfo['column'],
    #     padx=pdx, pady=pdy
    # )
    # Add details of what selected
    data_filetype_lbl['text'] = event.widget.get()
    data_filetype_lbl.grid()
    choose_data_fldr_btn['state'] = tk.NORMAL


def get_data_folder(filetype):
    path = askdirectory(title='Select data Folder')  # shows dialog box and return the path
    if (len(path)) > 0:  # Cancel not clicked
        btn_grid_info = choose_data_fldr_btn.grid_info()  # Get grid location of choose data folder button
        choose_data_fldr_btn.grid_remove()   # Remove choose data folder button
        # replace button with label
        data_fldr_frm.grid(
            row=btn_grid_info['row'],
            column=btn_grid_info['column'],
            padx=pdx, pady=pdy,
            columnspan=4
        )
        # Add label for path
        data_fldr_path_lbl['text'] = path
        data_fldr_path_lbl.grid(row=0, column=0, padx=pdx, pady=pdy, columnspan=4)
        # count number of files in folder with the correct extension
        f_type = filetype["file_type"][0]
        filelist = glob.glob(os.path.join(path, "*." + f_type))
        f_count = len(filelist)
        # make label visible and add text
        file_cue_lbl['text'] = f"{f_count} files with extension '{f_type}' found"
        file_cue_lbl.grid(row=1, column=0, padx=pdx, pady=pdy, columnspan=4)
        if f_count > 0:  # If some files were found, enable analysis
            run_analysis_btn['state'] = tk.NORMAL


def run_analysis():
    messagebox.showinfo(title="TO ADD", message="Run analysis not yet implemented")


def reset_window():
    # reset choose data file type
    choose_data_filetype_lbl.grid()
    data_filetype_combo.grid()
    data_filetype_frm.grid_remove()
    data_filetype_lbl.grid_remove()
    data_filetype_combo.set("")

    # reset data folder
    data_fldr_frm.grid_remove()
    data_fldr_path_lbl.grid_remove()
    choose_data_fldr_btn.grid()
    choose_data_fldr_btn['state'] = tk.DISABLED
    file_cue_lbl.grid_remove()
    # reset run analysis button
    run_analysis_btn['state'] = tk.DISABLED


# === START OF MAINLOOP ===
# create root window.
main_window = Tk()
main_window.title("Bulk file analyzer")
# x, y padding for tkinter objects
pdx = 5
pdy = 5

# Get data file definitions
data_file_definitions = get_file_definitions()  # Read in data file specifications
if type(data_file_definitions) is int:  # If script has returned an error code: exit
    quitScript()
file_import_settings = Get_filetype(data_file_definitions)
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
temp_btn = Button(main_window, text="Show", command=lambda :temp_show_info(file_import_settings))
temp_btn.pack()
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Get_filetype.
# choose_data_filetype_lbl.grid()
# create choose data file type label
choose_data_filetype_lbl = Label(main_window, text="Select data file type")
# choose_data_filetype_lbl.grid(row=0, column=0, padx=pdx, pady=pdy, sticky=tk.W)
# create chosen data file type labels but don't place in grid yet
data_filetype_frm = LabelFrame(main_window, text='Data file type')
data_filetype_lbl = Label(data_filetype_frm)

# create combobox object to select data file type
filetype_list = tk.StringVar()
data_filetype_combo = ttk.Combobox(main_window, textvariable=filetype_list, state='readonly')
data_filetype_combo['values'] = data_file_definitions['source'].tolist()  # convert to list to remove [] and ''
# data_filetype_combo['state'] = 'readonly'  # Prevent adding custom combobox values
# data_filetype_combo.bind('<<ComboboxSelected>>', data_filetype_selected)  # bind function for when value changed
# data_filetype_combo.grid(row=0, column=1, padx=pdx, pady=pdy, sticky=tk.W)

# create choose folder containing data button

choose_data_fldr_btn = ttk.Button(
    main_window,
    text="Select data folder",
    command=lambda: get_data_folder(data_file_definitions[data_file_definitions['source'] == filetype_list.get()]),
    state="disabled"
)
# choose_data_fldr_btn.grid(row=2, column=0, padx=pdx, pady=pdy, sticky=tk.W)

# create labels for data folder chosen and number of files cued but don't display yet
data_fldr_frm = LabelFrame(main_window, text="Data folder")
data_fldr_path_lbl = Label(data_fldr_frm)
file_cue_lbl = Label(data_fldr_frm)

# Create run analysis button
run_analysis_btn = ttk.Button(
    main_window,
    text="Run analysis",
    state="disabled",
    command=run_analysis
)

# Create reset button
reset_btn = ttk.Button(main_window, text="Reset", command=reset_window)
# reset_btn.grid(row=7, column=0, padx=pdx, pady=pdy)

# Create quit script button
quit_button = ttk.Button(main_window, text="Quit", command=quit_script)
# quit_button.grid(row=7, column=1, padx=pdx, pady=pdy)

# run_analysis_btn.grid(row=7, column=3, padx=pdx, pady=pdy)

# Display until User exits themselves.
main_window.mainloop()
