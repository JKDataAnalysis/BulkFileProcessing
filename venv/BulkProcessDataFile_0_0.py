# Import the library
from tkinter import *
# from tkinter import filedialog
from tkinter.filedialog import askdirectory
import os

# >>>> Check tkinter works across OSs

# 1) Select file types to load
# - Would be good to save a user preferences file, e.g. default file types to use.
# 2) Load relevant file specifications
# 3) Select folder to read data from
# 4) Read list of files of selected type from the foler into a df
# --- Start of loop
# L1) Read in first file
# L2) Process data in first file
# L3) Add results of processing to results df
# --- End of loop
# 5) Write results df to file


# File path
a = "myfile.txt"

# Check if the file exists
if os.path.exists(a):
    print("File exists")
else:
    print("File does not exist")

# Create an instance of window
win = Tk()

# Set the geometry of the window
win.geometry("700x300")

# Create a label
Label(win, text="Click the button to open a dialog", font='Arial 16 bold').pack(pady=15)


def chooseDirectory():
    path = askdirectory(title='Select data Folder')  # shows dialog box and return the path
    print(path)


# Function to open a file in the system
def open_file():
    filepath = filedialog.askopenfilename(title="Open a Text File", filetypes=(
    ("CSV files", "*.csv"), ("text files", "*.txt"), ("all files", "*.*")))
    file = open(filepath, 'r')
    print(file.read())
    file.close()


# Create a button to trigger the dialog
button = Button(win, text="Open", command=chooseDirectory)  # open_file)
button.pack()

win.mainloop()
