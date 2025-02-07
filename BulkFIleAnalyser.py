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
    root.destroy()
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


# class SourceType:


class BuildCue:
    def __init__(self, data_file_definitions):
        self.cued_file_count = 0  # Reset file counter

        # create choose source data file type label
        self.choose_data_source_type_lblfrm = LabelFrame(root, text="Select source data file type")
        self.choose_data_source_type_lblfrm.pack(padx=pdx, pady=pdy, side=tk.TOP, anchor=tk.NW)

        # create combobox object to select data file type
        defined_sources = tk.StringVar()
        self.source_type_combo = ttk.Combobox(self.choose_data_source_type_lblfrm, textvariable=defined_sources,
                                              state='readonly')
        self.source_type_combo['values'] = data_file_definitions['source'].tolist()
        self.source_type_combo.set("Choose data file type")
        self.source_type_combo.pack(padx=pdx, pady=pdy)
        self.source_type_combo.bind('<<ComboboxSelected>>', self.source_type_selected)

        # create choose data file type label
        choose_data_filetype_lblfrm = LabelFrame(root, text="Select data file type")
        choose_data_filetype_lblfrm.pack(padx=pdx, pady=pdy, side=tk.TOP, anchor=tk.NW)

        # Create a frame for file cue widgets
        data_files_lblfrm = LabelFrame(root, text="File cue")
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
        self.update_cue_count_lbl()

        main_btn_frame = tk.Frame(root, borderwidth=5, relief=tk.RAISED, bg='red', width=500)
        main_btn_frame.pack(side=tk.BOTTOM)

        # Create run analysis button
        self.run_analysis_btn = ttk.Button(
            main_btn_frame,
            text="Run analysis",
            state="disabled",
            command=self.run_analysis
        )
        self.run_analysis_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT)

        # Create reset button
        reset_btn = ttk.Button(
            main_btn_frame,
            text="Reset",
            command=self.reset_window)
        reset_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT)

        # Create quit script button
        quit_btn = ttk.Button(main_btn_frame, text="Quit", command=quit_script)
        quit_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT)

        # Set window to initial conditions
        self.reset_window()

    def source_type_selected(self, event):
        event.widget['state'] = tk.DISABLED  # Disable changing file type
        file_cue_info.add_files_btn['state'] = tk.NORMAL

    def add_files_btn_clicked(self):
        # Get the source file type selected in the combo box
        selected_source_type = self.source_type_combo.get()

        # Extract the matching file type and file type label
        file_type = data_file_definitions[data_file_definitions['source'] == selected_source_type]['file_type'][0]
        file_type_label = data_file_definitions[data_file_definitions['source'] == selected_source_type]['file_type_label'][0]
        self.add_files(file_type, file_type_label)

    def update_cue_count_lbl(self):
        self.cued_file_count_lbl.config(text=str(self.cued_file_count) + " files cued")

    def edit_cue(self, cued_file_list):
        # Create top level window
        self.file_cue_window = tk.Toplevel()
        self.file_cue_window.title('File cue')

        # Create listbox for cued files
        cue_list = tk.Variable(value=cued_file_list)
        self.file_list_listbox = tk.Listbox(self.file_cue_window, listvariable=cue_list, selectmode=EXTENDED, width=0)
        self.file_list_listbox.pack(padx=pdx, pady=pdy, expand=True, fill=tk.BOTH, side=LEFT)

        # Create frame for buttons
        edit_btn_frame = Frame(self.file_cue_window)
        edit_btn_frame.pack(side=tk.RIGHT, anchor=NE)

        # Create a button to remove selected files
        remove_selected_btn = ttk.Button(
            edit_btn_frame,
            text="Remove selected",
            command=self.remove_selected_clicked
        )
        remove_selected_btn.pack(padx=pdx, pady=pdy, side=TOP)

        # Create a button to save changes to list
        self.save_changes_btn = ttk.Button(
            edit_btn_frame,
            text="Save changes",
            command=self.save_changes_clicked,
            state=tk.DISABLED)
        self.save_changes_btn.pack(padx=pdx, pady=pdy, side=TOP)

        # Create a button to close (destroy) this window.
        close_btn = ttk.Button(
            edit_btn_frame,
            text="Close",
            command=self.file_cue_window.destroy)
        close_btn.pack(padx=pdx, pady=pdy, side=TOP)

    def remove_selected_clicked(self):
        files_selected = self.file_list_listbox.curselection()
        selected_count = len(files_selected)
        if selected_count == 0:
            messagebox.showinfo(title="no selection", message="No files selected")
        else:
            remove_selected_ok = messagebox.askokcancel(
                title="Remove selection",
                message=f"{selected_count} files will be removed from cue")
            if remove_selected_ok:  # User clicked OK
                for item in files_selected:
                    self.file_list_listbox.delete('active')
                self.save_changes_btn['state'] = tk.NORMAL

    def save_changes_clicked(self):
        # Set cue list to only those values still in list box
        self.cued_file_list = self.file_list_listbox.get(0, END)  # Get all the files still in tuple
        self.cued_file_count = len(self.cued_file_list)  # Update file count
        self.update_cue_count_lbl()  # Update file count label
        if self.cued_file_count == 0:  # If all files have been removed from cue, remove unavailable options
            self.run_analysis_btn['state'] = tk.DISABLED
            self.edit_files_btn['state'] = tk.DISABLED
        self.file_cue_window.destroy()  # Close the window
                
    def add_files(self, file_type, file_type_label):
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
        self.cued_file_list += selected_file_list
        # The difference between the tuple length (allow duplicates) and the set length (no duplicates) will be the
        # number of duplicates
        duplicate_count = len(self.cued_file_list) - len(set(self.cued_file_list))

        # Convert to a set then back to a tuple to remove duplicates
        self.cued_file_list = tuple(set(self.cued_file_list))
        self.cued_file_count = len(self.cued_file_list)
        msg_text = str(self.cued_file_count - duplicate_count) + " files added to cue"
        if duplicate_count > 0:
            msg_title = "Duplicates found"
            msg_text += "\n" + str(duplicate_count) + " file(s) found that are already cued\nThese will not be added"
        else:
            msg_title = "Files added"
        messagebox.showinfo(title=msg_title, message=msg_text)

        # If there are files in the cue, allow analysis to be run and cue to be viewed/ edited
        if self.cued_file_count > 0:
            self.run_analysis_btn['state'] = tk.NORMAL
            self.edit_files_btn['state'] = tk.NORMAL
        self.update_cue_count_lbl()

    def run_analysis(self):
        messagebox.showinfo(title="TO ADD", message="Run analysis not yet implemented")

    def reset_window(self):
        self.cued_file_list = tuple()  # Clear the file cue
        self.cued_file_count = 0  # Reset file counter
        self.update_cue_count_lbl()  # Update the displayed value
        self.source_type_combo['state'] = 'normal'  # Reactivate file type combo box
        self.add_files_btn['state'] = tk.DISABLED  # Disable add files button
        self.edit_files_btn['state'] = tk.DISABLED  # Disable view/ edit file cue button
        self.run_analysis_btn['state'] = tk.DISABLED  # Disable run analysis button


# def main():
# create root window.
root = Tk()
root.title("Bulk file analyzer")

# x, y padding for tkinter objects
pdx = 5
pdy = 5

# Get data file definitions
data_file_definitions = get_file_definitions()  # Read in data file specifications
if type(data_file_definitions) is int:  # If script has returned an error code: exit
    quit_script()

# Let user select source data file type
# source_type_info = SourceType(data_file_definitions['source'].tolist())

# Let user add files to analysis cue
file_cue_info = BuildCue(data_file_definitions)

# first_pass = True
# if first_pass:  # Initialise the window
#     first_pass = self.reset_window()

root.mainloop()
#
# if __name__ == '__main__':
#     main()