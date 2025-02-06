"""
TODO
    Look at changing source file definition file to csv. This would allow spaces in file type labels
    --- Start of loop
        * Read in first file
        * Process data in first file
        * Add results of processing to results df
    --- End of loop
    * Write results df to file
    * Add validation to read of data file definitions
    * Remove everything other then generic file definition from DataFileSPec.txt file. The script should by default
    should read all columns guessing their type and using first row as header. Variation in that should be possible by
    custom settings within the analysis script
    Known bugs
    ==========
    * Within SourceType.source_type_selected file_cue_info i.e. the class instance is referenced rather than self: This
    is generating a 'method may be static' error
    * BuildCue.edit_cue also giving 'method may be static' error as .self never used
    * add_files is currently outside of the BuildCue class and therefore the list of cued files does not exist outside
    of the function. It is not possible for the function to return a value as it is called from a callback function
    * See also Problems
"""
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


class SourceType:
    def __init__(self, source_type_list):
        # create choose data file type label
        self.choose_data_source_type_lblfrm = LabelFrame(main_window, text="Select source data file type")
        self.choose_data_source_type_lblfrm.pack(padx=pdx, pady=pdy, side=tk.TOP, anchor=tk.NW)

        # create combobox object to select data file type
        defined_sources = tk.StringVar()
        self.source_type_combo = ttk.Combobox(self.choose_data_source_type_lblfrm, textvariable=defined_sources, state='readonly')
        self.source_type_combo['values'] = source_type_list
        self.source_type_combo.set("Choose data file type")
        self.source_type_combo.pack(padx=pdx, pady=pdy)
        self.source_type_combo.bind('<<ComboboxSelected>>', self.source_type_selected)

    def source_type_selected(self, event):
        event.widget['state'] = tk.DISABLED  # Disable changing file type
        file_cue_info.add_files_btn['state'] = tk.NORMAL


class BuildCue:
    def __init__(self):
        # create choose data file type label
        choose_data_filetype_lblfrm = LabelFrame(main_window, text="Select data file type")
        choose_data_filetype_lblfrm.pack(padx=pdx, pady=pdy, side=tk.TOP, anchor=tk.NW)

        # Create a frame for file cue widgets
        data_files_lblfrm = LabelFrame(main_window, text="File cue")
        data_files_lblfrm.pack(padx=pdx, pady=pdy, side=tk.TOP, anchor=tk.NW)

        # Create a frame for build cue buttons
        build_cue_btn_frm = Frame(data_files_lblfrm)
        build_cue_btn_frm.pack(padx=pdx, pady=pdy, side=tk.TOP, anchor=tk.NW)

        # create button to add files
        self.add_files_btn = ttk.Button(
            build_cue_btn_frm,
            text="Add files",
            command=self.add_files_btn_clicked)
        self.add_files_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT, anchor=tk.NW)

        # create button to view/ edit file cue
        self.edit_files_btn = ttk.Button(
            build_cue_btn_frm,
            text="View/ edit cue",
            command=lambda: self.edit_cue(self.cued_file_list))
        self.edit_files_btn.pack(side=tk.LEFT, padx=pdx, pady=pdy)

        # Create label of files in cue
        cued_file_count = 0
        self.cued_file_count_lbl = Label(data_files_lblfrm)
        self.cued_file_count_lbl.pack(padx=pdx, pady=pdy, side=tk.BOTTOM, anchor=tk.NW)
        self.update_cue_count_lbl(cued_file_count)

    def add_files_btn_clicked(self):
        # Get the source file type selected in the combo box
        selected_source_type = source_type_info.source_type_combo.get()

        # Extract the matching file type and file type label
        file_type = data_file_definitions[data_file_definitions['source'] == selected_source_type]['file_type'][0]
        file_type_label = data_file_definitions[data_file_definitions['source'] == selected_source_type]['file_type_label'][0]
        add_files(file_type, file_type_label, self.cued_file_list)

    def update_cue_count_lbl(self, cued_file_count):
        self.cued_file_count_lbl.config(text=str(cued_file_count) + " files cued")

    def edit_cue(self, cued_file_list):
        print(cued_file_list)
        file_cue_window = tk.Toplevel()
        file_cue_window.title('File cue')
        cue_list = tk.Variable(value=cued_file_list)
        file_list_list = tk.Listbox(file_cue_window, listvariable=cue_list, selectmode=MULTIPLE, width=0)
        file_list_list.pack(padx=pdx, pady=pdy, expand=True, fill=tk.BOTH, side=LEFT)

        # Create frame for buttons
        edit_btn_frame = Frame(file_cue_window)
        edit_btn_frame.pack(side=tk.RIGHT, anchor=NE)

        # Create a button to remove selected files
        remove_selected_btn = ttk.Button(
            edit_btn_frame,
            text="Remove selected",
            command=print("Doesn't currently do anything")
        )
        remove_selected_btn.pack(padx=pdx, pady=pdy, side=TOP)

        # Create a button to close (destroy) this window.
        close_btn = ttk.Button(
            edit_btn_frame,
            text="Close",
            command=file_cue_window.destroy
        )
        close_btn.pack(padx=pdx, pady=pdy, side=TOP)


def add_files(file_type, file_type_label, cued_file_list):
    print(cued_file_list)
    filetypes = (
        (file_type_label, "*." + file_type),
        ('All files (may not be compatible)', '*.*')
    )
    selected_file_list = fd.askopenfilenames(
        title='Open files',
        # initialdir='/',
        filetypes=filetypes
    )
    if not type(selected_file_list) is tuple:  # Will be tuple unless user clicked cancel
        return
    print("returned as type: ", type(selected_file_list))
    print("returned as length: ", len(selected_file_list))
    cued_file_list += selected_file_list
    # The difference between the tuple length (allow duplicates) and the set length (no duplicates) will be the
    # number of duplicates
    duplicate_count = len(cued_file_list) - len(set(cued_file_list))
    # Convert to a set then back to a tuple to remove duplicates
    cued_file_list = tuple(set(cued_file_list))
    cued_file_count = len(cued_file_list)
    msg_text = str(cued_file_count - duplicate_count) + " files added to cue"
    if duplicate_count > 0:
        msg_title = "Duplicates found"
        msg_text += "\n" + str(duplicate_count) + " file(s) found that are already cued\nThese will not be added"
    else:
        msg_title = "Files added"
    messagebox.showinfo(title=msg_title, message=msg_text)

    # If there are files in the cue, allow analysis to be run and cue to be viewed/ edited
    if cued_file_count > 0:
        run_analysis_btn['state'] = tk.NORMAL
        file_cue_info.edit_files_btn['state'] = tk.NORMAL
    file_cue_info.update_cue_count_lbl(cued_file_count)


def run_analysis():
    messagebox.showinfo(title="TO ADD", message="Run analysis not yet implemented")


def reset_window():
    source_type_info.source_type_combo['state'] = 'normal'  # Reactivate file type combo box
    file_cue_info.add_files_btn['state'] = tk.DISABLED  # Disable add files button
    file_cue_info.edit_files_btn['state'] = tk.DISABLED  # Disable view/ edit file cue button
    run_analysis_btn['state'] = tk.DISABLED  # Disable run analysis button
    file_cue_info.cued_file_list = tuple()   # Clear the file cue
    file_cue_info.update_cue_count_lbl(len(file_cue_info.cued_file_list))  # Update the displayed value
    return False  # return flag that window has been initialised


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

# Let user select source data file type
source_type_info = SourceType(data_file_definitions['source'].tolist())

# Let user add files to analysis cue
file_cue_info = BuildCue()

# temp_btn = ttk.Button(main_window, text="filetype", command=print_filetype)
# temp_btn.pack()
# cue = BuildCue
# add_files_btn = build_cue()
# # add_files_btn.(self.import_settings['file_type'][0]),
# add_files_btn.pack(side=tk.TOP, padx=pdx, pady=pdy)


# file_import_settings = GetFiles(data_file_definitions)

main_btn_frame = tk.Frame(main_window, borderwidth=5, relief=tk.RAISED, bg='red', width=500)
main_btn_frame.pack(side=tk.BOTTOM)

# Create run analysis button
run_analysis_btn = ttk.Button(
    main_btn_frame,
    text="Run analysis",
    state="disabled",
    command=run_analysis
)
run_analysis_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT)

# Create reset button
reset_btn = ttk.Button(
    main_btn_frame,
    text="Reset",
    command=lambda: reset_window(
        # file_import_settings.data_filetype_combo,
        # file_import_settings.add_files_btn,
        # file_import_settings.edit_files_btn
    )
)
reset_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT)
# reset_btn.grid(row=7, column=0, padx=pdx, pady=pdy)

# Create quit script button
quit_btn = ttk.Button(main_btn_frame, text="Quit", command=quit_script)
quit_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT)
# quit_button.grid(row=7, column=1, padx=pdx, pady=pdy)

run_analysis_btn.pack(padx=pdx, pady=pdy, side=tk.RIGHT)
# run_analysis_btn.grid(row=7, column=3, padx=pdx, pady=pdy)
# Display until User exits themselves.

first_pass = True
if first_pass:  # Initialise the window
    first_pass = reset_window()

main_window.mainloop()
