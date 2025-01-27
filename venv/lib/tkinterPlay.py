'''
Done so far
===========
* Read in data file definitions
* Allow user to select from defined data file types
TODO
====
Lots!
* Add validation to read of data file definitions
* Create main screen
    - Select data files
    - Change data file type (save last chosen to a user preferences file)
* Remove option of loading another data file definition file if the default is not found 
    (but this code can be reused for selecting data file folders)
* Select folder to read data from
* Read list of files of selected type from the folder into a df
--- Start of loop
    * Read in first file
    * Process data in first file
    * Add results of processing to results df
--- End of loop
* Write results df to file
Known bugs
==========
* The data file types listed in listbox include the []s at start and end and names are quoted
'''

import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
# import pandas as pd
import numpy as np

import os
import sys

# from tkinter import ttk
from tkinter import *
from tkinter.messagebox import CANCEL, RETRY

def quitScript():
    print("Leaving program")
    chooseDataFileType.destroy()
    exit()

def okClicked(selected):
    chooseDataFileType.destroy()
    print(dataFileDefs[selected[0]])

# Read data file definition file
def get_file_defs():
    dataDefFile = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "DataFileSpec.txt") # Set file to default location and name
    while not os.path.exists(dataDefFile):  # If the default file exists use it
        dataDefFile = fd.askopenfilename(
            title="Open data file definition file",
            filetypes=(("CSV files", "*.csv"), ("text files", "*.txt"), ("all files", "*.*"))
        )
        if len(dataDefFile) == 0: # no file selected or user clicked Cancel
            askRetry = messagebox.askretrycancel(title="Failed to read data file definitions",
                                   message="No data file specifications selected\nThis is required to proceed",
                                   default=RETRY)
            if not askRetry: # Cancel clicked- quit the program
                return -1
            else:
                dataDefFile=""
    # df = pd.read_csv(dataDefFile, header=1)
    arr = np.genfromtxt(dataDefFile, comments='#', names=True, dtype=None)
    return arr

# create a root window.
chooseDataFileType = Tk()
dataFileDefs = get_file_defs() # Read in data file specifications
if type(dataFileDefs) == int: # If script has returned an error code- exit
    quitScript()
fileTypeList = tk.Variable(value=dataFileDefs['source'])
# Set width of list box to length of longest source name + packing to a maximum of 50
listBoxWidth = min(len(max(dataFileDefs['source'], key = len)) + 3, 50)

# create listbox object
listbox = Listbox(chooseDataFileType,
                  listvariable=fileTypeList,
                  height=10,
                  width=listBoxWidth,
                  bg="white",
                  activestyle= 'dotbox',
                  font="Helvetica",
                  fg="black")

# Define the size of the window.
chooseDataFileType.geometry("300x250")

# Define a label for the list.
label = Label(chooseDataFileType, text=" Select source data file type")
btn = Button(chooseDataFileType,
             # command=print(listbox.curselection()),
             command=lambda: okClicked(listbox.curselection()),
             text="OK")

# pack the widgets
label.pack()
listbox.pack()
btn.pack()

# Display until User
# exits themselves.
chooseDataFileType.mainloop()


