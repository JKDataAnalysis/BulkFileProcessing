import tkinter as tk
# from tkinter import ttk
from tkinter import *

fileTypes = ("Footscan SAM",
             "Bioware Ax, Ay",
             "Bioware Ax, Ay, Fz",
             "Bioware Ax, Ay, Fx, Fy, Fz" )


def okClicked(selected):
	print(fileTypes[selected[0]])


# create a root window.
top = Tk()

fileTypeList = tk.Variable(value=fileTypes)

# create listbox object
listbox = Listbox(top,
                  listvariable=fileTypeList,
                  height=10,
                  width=15,
                  bg="grey",
                  activestyle='dotbox',
                  font="Helvetica",
                  fg="yellow")

# Define the size of the window.
top.geometry("300x250")

# Define a label for the list.
label = Label(top, text=" Select source data file type")

# >>>> Modify this to populate with possible file types read from file.
# insert elements by their
# index and names.
# listbox.insert(1, "FootscanSAM")
# listbox.insert(2, "BiowareAxAy")
# listbox.insert(3, "BiowareAxAyFz")
# listbox.insert(4, "BiowareAxAyFxFyFz")

btn = Button(top,
             # command=print(listbox.curselection()),
             command=lambda: okClicked(listbox.curselection()),
             text="OK")

# pack the widgets
label.pack()
btn.pack()
listbox.pack()

# Display until User
# exits themselves.
top.mainloop()


