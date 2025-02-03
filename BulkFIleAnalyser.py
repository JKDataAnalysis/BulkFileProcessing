'''
TODO
    + Look at binding multiple functions so that updating the window does not need to be within the class definition
    * Resolve remaining problems including instance attribution outside of __init__
    * Modify get path function as a class to return list of files of set type within the chosen folder
    (See Test01.py)
    * (Add button to show and edit file list)
    * Add validation to read of data file definitions
    --- Start of loop
        * Read in first file
        * Process data in first file
        * Add results of processing to results df
    --- End of loop
    * Write results df to file
    Known bugs
    ==========
'''
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import ttk
import numpy as np
import os
import sys
from tkinter import *


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


class GetFiles:
    def __init__(self, defined_filetypes):
        self.file_defs = defined_filetypes  # Copy passed filetypes so they will be available for other class functions
        self.type_list = defined_filetypes['source'].tolist()   # Strip out list of defined source types
        # create choose data file type label
        choose_data_filetype_lblfrm = LabelFrame(main_window, text="Select data file type")
        choose_data_filetype_lblfrm.pack(padx=pdx, pady=pdy, side=tk.TOP, anchor=tk.NW)

        # create combobox object to select data file type
        defined_types = tk.StringVar()
        # create combobox with self. so it can be used in the reset function
        self.data_filetype_combo = ttk.Combobox(choose_data_filetype_lblfrm, textvariable=defined_filetypes, state='readonly')
        self.data_filetype_combo['values'] = self.type_list
        self.data_filetype_combo.bind('<<ComboboxSelected>>', self.get_import_file_defs)  # bind function for when value changed
        self.data_filetype_combo.pack(padx=pdx, pady=pdy)

        # Create a frame for file cue widgets
        data_files_lblfrm = LabelFrame(main_window, text="File cue")
        data_files_lblfrm.pack(padx=pdx, pady=pdy, side=tk.TOP, anchor=tk.NW)
        # create button to add files
        self.add_files_btn = ttk.Button(
            data_files_lblfrm,
            text="Add files",
            command=lambda: self.add_files(self.import_settings['file_type'][0]),
            state="disabled"
        )
        self.add_files_btn.pack(side=tk.TOP, padx=pdx, pady=pdy)
        # create button to view/ edit file cue
        self.edit_files_btn = ttk.Button(
            data_files_lblfrm,
            text="View/ edit cue",
            command=lambda: self.edit_cue(self.cued_file_list),
            state="disabled"
        )
        self.edit_files_btn.pack(side=tk.TOP, padx=pdx, pady=pdy)

        # Create label of files in cue
        self.cued_file_count = 0
        self.cued_file_count_lbl = Label(data_files_lblfrm)
        self.update_cue()
        self.cued_file_count_lbl.pack(side=tk.TOP, padx=pdx, pady=pdy)

    def get_import_file_defs(self, event):
        self.import_settings = self.file_defs[self.file_defs['source'] == event.widget.get()]
        event.widget['state'] = 'disabled'  # Disable combox box so that filetype can't be changed after folder is selected
        self.add_files_btn['state'] = 'normal'   # Enable the data folder button

    def add_files(self, file_type):
        filetypes = (
            ('Files of type in definitions', "*." + file_type),
            ('All files (may not be compatible)', '*.*')
        )
        selected_file_list = fd.askopenfilenames(
            title='Open files',
            # initialdir='/',
            filetypes=filetypes
        )
        try:  # If a cue has already been created, add the files to it
            self.cued_file_list += selected_file_list
        except AttributeError:  # If no existing cue, create a tuple for it
            self.cued_file_list = selected_file_list

        # The difference between the tuple length (allow duplicates) and the set length (no duplicates) will be the
        # number of duplicates
        duplicate_count = len(self.cued_file_list) - len(set(self.cued_file_list))
        if duplicate_count > 0:
            messagebox.showinfo(
                title="Duplicates found",
                message=f"{str(duplicate_count)} file(s) found that are already cued\nThese will not be added"
            )
            # Convert to a set then back to a tuple to remove duplicates
            self.cued_file_list = tuple(set(self.cued_file_list))
        self.cued_file_count = len(self.cued_file_list)
        if self.cued_file_count > 0:  # If there are files in the cue, allow analysis to be run
            run_analysis_btn['state'] = 'normal'
            self.edit_files_btn['state']= 'normal'
        self.update_cue()

    def update_cue(self):
        self.cued_file_count_lbl.config(text=str(self.cued_file_count) + " files cued")

    def edit_cue(self, file_list):
        file_cue_window = tk.Toplevel()
        file_cue_window.title('File cue')
        cue_list = tk.Variable(value=file_list)
        file_list_list = tk.Listbox(file_cue_window, listvariable=cue_list, selectmode=MULTIPLE, width=0)
        file_list_list.pack(expand=True, fill=tk.BOTH, padx=pdx, pady=pdy)
        # Create a button to close (destroy) this window.
        button_close = ttk.Button(
            file_cue_window,
            text="Close window",
            command=file_cue_window.destroy
        )
        button_close.pack(padx=pdx, pady=pdy)


def run_analysis():
    messagebox.showinfo(title="TO ADD", message="Run analysis not yet implemented")


def reset_window(filetype_combo, add_files_btn, edit_files_btn):
    filetype_combo['state'] = 'normal'  # Reactivate file type combo box
    add_files_btn['state'] = tk.DISABLED  # Disable add files button
    edit_files_btn['state'] = tk.DISABLED  # Disable view/ edit file cue button
    run_analysis_btn['state'] = tk.DISABLED  # Disable run analysis button
    file_import_settings.cued_file_list = tuple()   # Clear the file cue
    file_import_settings.cued_file_count = 0    # zero the file cue length
    file_import_settings.update_cue()   # Update the displayed cue length


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
    quit_script()
file_import_settings = GetFiles(data_file_definitions)

btn_frame = tk.Frame(main_window, borderwidth=5, relief=tk.RAISED, bg='red', width=500)
btn_frame.pack(side=tk.BOTTOM)

# Create run analysis button
run_analysis_btn = ttk.Button(
    btn_frame,
    text="Run analysis",
    state="disabled",
    command=run_analysis
)
run_analysis_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT)

# Create reset button
reset_btn = ttk.Button(
    btn_frame,
    text="Reset",
    command=lambda: reset_window(
        file_import_settings.data_filetype_combo,
        file_import_settings.add_files_btn,
        file_import_settings.edit_files_btn
    )
)
reset_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT)
# reset_btn.grid(row=7, column=0, padx=pdx, pady=pdy)

# Create quit script button
quit_btn = ttk.Button(btn_frame, text="Quit", command=quit_script)
quit_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT)
# quit_button.grid(row=7, column=1, padx=pdx, pady=pdy)

run_analysis_btn.pack(padx=pdx, pady=pdy, side=tk.RIGHT)
# run_analysis_btn.grid(row=7, column=3, padx=pdx, pady=pdy)
# Display until User exits themselves.


main_window.mainloop()
