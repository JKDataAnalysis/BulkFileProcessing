'''
Done so far
===========
* Read in data file definitions
* Created main screen
    - Button to select data files
        - returns list of files of type defined in data file definitions
    - Label: n data files in selected folder
    - ComboBox: data file type (save last chosen to a user preferences file)
        - Allows user to select from defined data file types
    - Button: Start analysis: run the thing
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
    * The number of files cued for analysis currently does not update when a data folder is chosen
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


# def data_filetype_changed():
#     typ = dataFileDefs[dataFileDefs['source']== filetypelist.get()]
#     chooseDataFileType.destroy()
#     print (typ)


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
    if (len(path)) > 0: # Cancel not clicked
        filelist = glob.glob(os.path.join(path, "*." + filetype["file_type"][0]))
        print(filelist)

# create root window.
mainwindow = Tk()
mainwindow.geometry("400x250")
mainwindow.title("Bulk file analyzer")

pdx = 5; pdy = 5 # x, y padding for tkinter objects

# Get data file definitions
dataFileDefs = get_file_defs()  # Read in data file specifications
if type(dataFileDefs) == int:  # If script has returned an error code- exit
    quitScript()

# create data file type label
datafiletype_label = Label(mainwindow, text="Data file type")
datafiletype_label.grid(row=0, column=1, padx=pdx, pady=pdy)

# create combobox object to select data file type
filetypelist = tk.StringVar()
datafiletype_combo = ttk.Combobox(mainwindow, textvariable=filetypelist, state='readonly')
datafiletype_combo['values']= value=dataFileDefs['source'].tolist() # convert to list to remove [] and ''
datafiletype_combo['state'] = 'readonly' # Prevent adding custom combobox values
datafiletype_combo.current(0) # Set default value >>>> This should be changed to set it to the last used value
datafiletype_combo.grid(row=0, column=2, padx=pdx, pady=pdy)
# datafiletypelist.bind('<<ComboboxSelected>>', data_filetype_changed) # bind function for when value changed

# create choose folder containing data button
choosedatafolder_button = ttk.Button(
    mainwindow,
    text = "Select data folder",
    command = lambda: getdatafolder(dataFileDefs[dataFileDefs['source']== filetypelist.get()])
)
choosedatafolder_button.grid(row=2, column=1, padx=pdx, pady=pdy)

# create label of number of files cued
filecue_label = Label(mainwindow, text="<FIX THIS>" + " files cued")
filecue_label.grid(row=2, column=2, padx=pdx, pady=pdy)

# Create run analysis button
runanalysis_button = ttk.Button(mainwindow, text = "Run analysis", state="disabled")
runanalysis_button.grid(row=3, column=1, padx=pdx, pady=pdy)

# Create quit script button
quit_button = ttk.Button(mainwindow, text = "Quit", command = lambda: quitscript())
quit_button.grid(row=4, column=1, padx=pdx, pady=pdy)

# Display until User exits themselves.
mainwindow.mainloop()
