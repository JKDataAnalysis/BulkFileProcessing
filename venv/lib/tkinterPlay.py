'''
Done so far
===========
* Read in data file definitions
* Created main screen
    - ComboBox: select data file type
        - Allows user to select from defined data file types
    - Button to select data folder containing data files
    - Label: n data files in selected folder
    - Button: Start analysis: run the thing
        - NOT YET IMPLEMENTED
    - Button: Reset window
        - clears set values
    - Button: Quit script
TODO
====
* Add validation to read of data file definitions
* Create subclass of tkinter button class to return values of selected data folder and number of files cued
* Read list of files of selected type from the folder into a df
--- Start of loop
    * Read in first file
    * Process data in first file
    * Add results of processing to results df
--- End of loop
* Write results df to file
Known bugs
    * FIXED: The number of files cued for analysis currently does not update when a data folder is chosen
    * The displayed folder will cause the grid column to resize pushing the reset and quit buttons off the window
        - This is alleviated with rowspan but need ot look at containers to place info and buttons separately
==========
'''
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


# from tkinter.messagebox import CANCEL, RETRY

def quitscript():
    print("Leaving program")
    mainwindow.destroy()
    exit()


# Read data file definition file
# def get_file_defs():
#     dataDefFile = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "DataFileSpec.txt") # Set file to default location and name
#     while not os.path.exists(dataDefFile):  # If the default file exists use it
#         dataDefFile = fd.askopenfilename(
#             title="Open data file definition file",
#             filetypes=(("CSV files", "*.csv"), ("text files", "*.txt"), ("all files", "*.*"))
#         )
#         if len(dataDefFile) == 0: # no file selected or user clicked Cancel
#             askRetry = messagebox.askretrycancel(title="Failed to read data file definitions",
#                                    message="No data file specifications selected\nThis is required to proceed",
#                                    default=RETRY)
#             if not askRetry: # Cancel clicked- quit the program
#                 return -1
#             else:
#                 dataDefFile=""
#     # df = pd.read_csv(dataDefFile, header=1)
#     arr = np.genfromtxt(dataDefFile, comments='#', names=True, dtype=None)
#     return arr
def get_file_defs():
    datadeffile = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),
                               "DataFileSpec.txt")  # Set file to default location and name
    if os.path.exists(datadeffile):  # If the default file exists
        arr = np.genfromtxt(
            datadeffile,
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
            detail="Search path:\n" + datadeffile,
            icon='error'
        )
        return -1


def getdatafolder(filetype):
    path = askdirectory(title='Select data Folder')  # shows dialog box and return the path
    if (len(path)) > 0:  # Cancel not clicked
        filelist = glob.glob(os.path.join(path, "*." + filetype["file_type"][0]))
        # Get button grid position and then remove it
        button_grid_info = choosedatafolder_button.grid_info() # Get grid location of choosedatafolder_button
        choosedatafolder_button.grid_remove() # Remove button
        # replace button with label
        chosendatafolder_label['text'] = f"Selected data folder:\n {path}"
        chosendatafolder_label.grid(
            row=button_grid_info['row'],
            column=button_grid_info['column'],
            padx=pdx, pady=pdy,
            columnspan = 4
        )

        # count number of files in folder with the correct extension
        ftype = filetype['file_type'][0]
        fcount = 0
        for file in os.listdir(path):
            if file.endswith(ftype):
                fcount += 1
        # make label visible and add text
        filecue_label['text'] = f"{fcount} files with extension '{ftype}' found in selected folder"
        filecue_label.grid(row=button_grid_info['row']+1, column=button_grid_info['column'], padx=pdx, pady=pdy, columnspan = 4)
        if fcount > 0: # If some files were found, enable analysis
            runanalysis_button['state'] = tk.NORMAL

def datafiletype_selected(selected):
    filetypelabel_gridinfo =choosedatafiletype_label.grid_info()
    selecteddatafiletype_label.grid(row = filetypelabel_gridinfo['row'], column = filetypelabel_gridinfo['column']    )
    choosedatafiletype_label.grid_remove()
    datafiletype_combo.grid_remove()
    selecteddatafiletype_label['text'] = 'Data file type selected: ' + filetypelist.get()
    choosedatafolder_button['state'] = tk.NORMAL


def run_analysis():
    print("Run analysis: still need to do this!")

def reset_window():
    # reset choose data file type
    choosedatafiletype_label.grid()
    datafiletype_combo.grid()
    selecteddatafiletype_label.grid_remove()
    datafiletype_combo.set("")

    # reset data folder
    chosendatafolder_label.grid_remove()
    choosedatafolder_button.grid()
    choosedatafolder_button['state'] = tk.DISABLED
    filecue_label.grid_remove()

    # reset run analysis button
    runanalysis_button['state'] = tk.DISABLED

# === START OF MAINLOOP ===
# create root window.
mainwindow = Tk()
mainwindow.geometry("450x200")
mainwindow.title("Bulk file analyzer")

pdx = 5;
pdy = 5  # x, y padding for tkinter objects

# Get data file definitions
dataFileDefs = get_file_defs()  # Read in data file specifications
if type(dataFileDefs) == int:  # If script has returned an error code- exit
    quitScript()

# create choose data file type label
choosedatafiletype_label = Label(mainwindow, text="Select data file type")
choosedatafiletype_label.grid(row=0, column=1, padx=pdx, pady=pdy)
# create chosen data file type label but don't label of place in grid yet
selecteddatafiletype_label = Label(mainwindow)

# create combobox object to select data file type
filetypelist = tk.StringVar()
datafiletype_combo = ttk.Combobox(mainwindow, textvariable=filetypelist, state='readonly')
datafiletype_combo['values'] = value = dataFileDefs['source'].tolist()  # convert to list to remove [] and ''
datafiletype_combo['state'] = 'readonly'  # Prevent adding custom combobox values
datafiletype_combo.bind('<<ComboboxSelected>>', datafiletype_selected)  # bind function for when value changed
datafiletype_combo.grid(row=0, column=2, padx=pdx, pady=pdy)

# create choose folder containing data button
choosedatafolder_button = ttk.Button(
    mainwindow,
    text="Select data folder",
    command=lambda: getdatafolder(dataFileDefs[dataFileDefs['source'] == filetypelist.get()]),
    state="disabled"
)
choosedatafolder_button.grid(row=2, column=1, padx=pdx, pady=pdy)

# create label of data folder chosen but don't display it or add text yet
chosendatafolder_label = Label(mainwindow)

# create label of number of files cued but don't display it or add text yet
filecue_label = Label(mainwindow)

# Create run analysis button
runanalysis_button = ttk.Button(
    mainwindow,
    text="Run analysis",
    state="disabled",
    command = run_analysis
)
runanalysis_button.grid(row=5, column=1, padx=pdx, pady=pdy)

# Create quit script button
quit_button = ttk.Button(mainwindow, text="Quit", command=lambda: quitscript())
quit_button.grid(row=5, column=3, padx=pdx, pady=pdy)

# Create reset button
reset_button = ttk.Button(mainwindow, text="Reset", command=reset_window)
reset_button.grid(row=5, column=2, padx=pdx, pady=pdy)

# Display until User exits themselves.
mainwindow.mainloop()
