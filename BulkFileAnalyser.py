"""
TODO
    ====================
    Questions to resolve
    ====================
    * Is it possible to pass a variable number of parameters to pd.read_csv so that not all possible import parameters
    need to be set in the import settings file?
    * How to read dtype (key value pairs) from csv file?
    * Can't set both nrows and skipfooter in pd.read_csv. How can either of those options be given to users without
    causing (or just supressing) errors? Have standard read in this file and custom in AnalysisTemplate file with a flag
    (use_custom_file_read) set in the Analysis Template?
    =====
    Major
    =====
    * Create window to run analysis- just show progress bar and label
        - Once complete show options for results- save as / view
    --- Start of loop
        * Read in file
        * Process data in first file
        * Add results of processing to results df
    --- End of loop
    * Write results df to file
    =====
    Minor
    =====
    * padx and pady values are currently set within the classes rather than being passed to them
    * Vertical scroll bar on edit files listbox should only display if the number of files displayed is greater than the
     listbox height
    * default_dir to start looking for data files is temporarily set to location of tekscan test data. This should be
    the last used folder
    ==========
    Known bugs
    ==========
    * Some of the Tekscan data files have more than 1 data set in them. This will results in rows containing text in
    rows that are defined as numeric types. A utility could be quite easily written to identify and correct these but,
    given that I'm not likely to be using Tekscan data any time soon, this probably doesn't need to be done and
    certainly not as part of this script. Do need to make the script more robust in handling such errors though as they
    could be encountered in other files
"""

import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import ttk
from xml.etree.ElementInclude import include

import pandas as pd
import os
import sys
from tkinter import *
import glob

# import numpy as np

# import AnalysisTemplate
# from AnalysisTemplate import external_read_info


def get_file_definitions(expected_no_def_cols):
    # Set file to default location and name
    data_def_file = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "DataFileSpec.csv")
    if os.path.exists(data_def_file):  # If the default file exists
        arr = pd.read_csv(data_def_file, delimiter=",")  # Read it into a df
        if arr.shape[0] >= 1 and arr.shape[1] == expected_no_def_cols:  # Check at least 1 source type and correct number of columns read
            return arr
        else:
            messagebox.showerror(
                title="Failed to read data file definitions",
                message="Aborting: Error in data file definitions found",
                detail=f"Expected at least 1 row of {expected_no_def_cols} columns\nGot {arr.shape[0]} rows of {arr.shape[1]}",
                icon='error'
            )
            return -2
    else:
        messagebox.showerror(
            title="Failed to read data file definitions",
            message="Aborting: No data file definitions found",
            detail="Search path:\n" + data_def_file,
            icon='error'
        )
        return -1


class BuildCue(tk.Frame):
    def __init__(self, data_file_definitions, master=None, **kwargs):
        super().__init__(master, **kwargs)
    # def __init__(self, data_file_definitions):
        self.file_import_settings = None
        self.cued_file_list = None
        self.cued_file_count = 0  # Reset file counter
        self.data_file_defs = data_file_definitions

        # x, y padding for tkinter objects
        pdx = 5
        pdy = 5

        # create choose source data file type label
        self.choose_data_source_type_lblfrm = LabelFrame(self, text="Select source data file type")
        self.choose_data_source_type_lblfrm.pack(padx=pdx, pady=pdy, side=tk.TOP, anchor=tk.NW)

        # create combobox object to select data file type
        defined_sources = tk.StringVar()
        self.source_type_combo = ttk.Combobox(self.choose_data_source_type_lblfrm, textvariable=defined_sources,
                                              state='readonly')
        self.source_type_combo['values'] = self.data_file_defs['source'].tolist()
        self.source_type_combo.set("Choose data file type")
        self.source_type_combo.pack(padx=pdx, pady=pdy)
        self.source_type_combo.bind('<<ComboboxSelected>>', self.source_type_selected)

        # create choose data file type label
        choose_data_filetype_lblfrm = LabelFrame(self, text="Select data file type")
        choose_data_filetype_lblfrm.pack(padx=pdx, pady=pdy, side=tk.TOP, anchor=tk.NW)

        # Create a frame for file cue widgets
        data_files_lblfrm = LabelFrame(self, text="File cue")
        data_files_lblfrm.pack(padx=pdx, pady=pdy, side=tk.TOP, anchor=tk.NW)

        # Create a frame for build cue buttons
        build_cue_btn_frm = Frame(data_files_lblfrm)
        build_cue_btn_frm.pack(padx=pdx, pady=pdy, side=tk.TOP, anchor=tk.NW)

        # create button to add files
        self.add_files_btn = ttk.Button(
            build_cue_btn_frm,
            text="Select files",
        command=lambda: self.add_files_btns_clicked("files"))
        self.add_files_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT, anchor=tk.NW)

        # Create button to add folder
        self.add_folder_btn = ttk.Button(
            build_cue_btn_frm,
            text="Add ALL files in folder",
            command=lambda: self.add_files_btns_clicked("folder"))
        # self.add_folder_btn.bind("<Button-1>", lambda x: self.add_files_btns_clicked("folder"))
        self.add_folder_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT, anchor=tk.NW)

        # Create checkbox to include subfolders
        self.include_subs = tk.BooleanVar()
        self.include_subdir_chk = ttk.Checkbutton(
            build_cue_btn_frm,
            text="Include\nsubfolders",
            variable=self.include_subs)
        self.include_subdir_chk.pack(padx=pdx, pady=pdy, side=tk.LEFT, anchor=tk.NW)

        # create button to view/ edit file cue
        self.edit_files_btn = ttk.Button(
            build_cue_btn_frm,
            text="View/ edit cue",
            command=self.edit_cue_clicked)
        self.edit_files_btn.pack(side=tk.LEFT, padx=pdx, pady=pdy)

        # Create label of files in cue
        self.cued_file_count_lbl = Label(data_files_lblfrm)
        self.cued_file_count_lbl.pack(padx=pdx, pady=pdy, side=tk.BOTTOM, anchor=tk.NW)
        self.update_cue_count_lbl()

        main_btn_frame = tk.Frame(self)
        main_btn_frame.pack(side=tk.BOTTOM)

        # Create reset button
        reset_btn = ttk.Button(
            main_btn_frame,
            text="Reset",
            command=self.reset_window)
        reset_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT)

        # Create quit script button
        quit_btn = ttk.Button(main_btn_frame, text="Quit", command=self.quit_script)
        quit_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT)

        # Create run analysis button
        self.run_analysis_btn = ttk.Button(
            main_btn_frame,
            text="Run analysis",
            state="disabled",
            command=self.run_analysis_clicked)
        self.run_analysis_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT)

        # Set window to initial conditions
        self.reset_window()

    def source_type_selected(self, event):
        event.widget['state'] = tk.DISABLED  # Disable changing file type
        # Enable adding files/ folders and whether subfolders are to be included
        self.add_files_btn['state'] = tk.NORMAL
        self.add_folder_btn['state'] = tk.NORMAL
        self.include_subdir_chk['state'] = tk.NORMAL

    def add_files_btns_clicked(self, path_type):
        # Get the source file type selected in the combo box
        selected_source_type = self.source_type_combo.get()

        # Get the import settings for the selected source file type
        self.file_import_settings = self.data_file_defs.loc[self.data_file_defs['source'] == selected_source_type]
        # Flatten to a pandas series
        self.file_import_settings = self.file_import_settings.squeeze()

        # Extract the matching file type and file type label
        file_type = self.file_import_settings['file_type']
        file_type_label = self.file_import_settings['file_type_label']

        if path_type == "files":  # Add files button clicked
            self.add_files(file_type, file_type_label)
        elif path_type == "folder":  # Add folders button clicked
            self.add_folder(file_type)
        else:  # How the hell did we get here?
            messagebox.showerror(
                title="Button callback function error",
                message="Function called by file button is not recognised")
            self.quit_script()

    def add_files_to_cue(self, file_list):
        passed_file_count = len(file_list)

        self.cued_file_list += file_list

        # The difference between the tuple length (allow duplicates) and the set length (no duplicates) will be the
        # number of duplicates
        duplicate_count = len(self.cued_file_list) - len(set(self.cued_file_list))

        # Convert to a set then back to a tuple to remove duplicates
        self.cued_file_list = tuple(set(self.cued_file_list))
        self.cued_file_count = len(self.cued_file_list)
        msg_text = str(passed_file_count - duplicate_count) + " files added to cue"
        if duplicate_count > 0:
            msg_title = "Duplicates found"
            msg_text += "\n" + str(
                duplicate_count) + " file(s) found that are already cued\nThese will not be added"
        else:
            msg_title = "Files added"
        messagebox.showinfo(title=msg_title, message=msg_text)

        # If there are files in the cue, allow analysis to be run and cue to be viewed/ edited
        if self.cued_file_count > 0:
            self.run_analysis_btn['state'] = tk.NORMAL
            self.edit_files_btn['state'] = tk.NORMAL
        self.update_cue_count_lbl()

    def add_files(self, file_type, file_type_label):
        filetypes = (
            (file_type_label, "*." + file_type),
            ('All files (may not be compatible)', '*.*')
        )
        default_dir = '/home/jon/Documents/TestData/RecentData'
        selected_file_list = fd.askopenfilenames(
            title='Open files',
            initialdir=default_dir,
            filetypes=filetypes
        )
        if not type(selected_file_list) is tuple:  # Will be tuple unless user clicked cancel
            return
        self.add_files_to_cue(selected_file_list)  # Remove duplicates and update count

    def add_folder(self,  file_type):
        default_dir = '/home/jon/Documents/TestData/RecentData'
        selected_folder = fd.askdirectory(
            title='Open files',
            initialdir=default_dir,
            mustexist=True
        )
        if not os.path.isdir(selected_folder):  # Will be unless user clicked cancel
            return

        file_list = list(self.cued_file_list)  # Start with existing tuple of files (as list)
        # Combine chosen folder path with wildcard and passed file type
        if self.include_subs.get():
            add_subs = "**"
        else:
            add_subs = ""
        file_filter = os.path.join(selected_folder, add_subs, "*." + file_type)
        files = glob.glob(file_filter, recursive=self.include_subs.get())  # Get list of matching files and folders
        for f in files:  # Add only files (not directories)
            if os.path.isfile(f):
                file_list.append(f)
        # self.cued_file_list = tuple(file_list)  # Convert back to tuple
        self.add_files_to_cue(tuple(file_list))  # As tuple to match what add files will produce

    def run_analysis_clicked(self):
        results_df = RunAnalysis(self.cued_file_list, self.file_import_settings, self)

    def reset_window(self):
        self.cued_file_list = tuple()  # Clear the file cue
        self.cued_file_count = 0  # Reset file counter
        self.update_cue_count_lbl()  # Update the displayed value
        self.source_type_combo['state'] = tk.NORMAL  # Reactivate file type combo box
        self.add_files_btn['state'] = tk.DISABLED  # Disable add files button
        self.add_folder_btn['state'] = tk.DISABLED  # Disable add folder button
        self.include_subdir_chk['state'] = tk.DISABLED  # Disable include subfolders checkbox
        self.edit_files_btn['state'] = tk.DISABLED  # Disable view/ edit file cue button
        self.run_analysis_btn['state'] = tk.DISABLED  # Disable run analysis button

    def edit_cue_clicked(self):
        # self.file_cue_window.title('File cue')
        edited_file_list = EditCue(self.cued_file_list, self)  # Create pop-up for editing list
        if edited_file_list.saved_changes:  # Changes have been made and saved
            self.cued_file_list = edited_file_list.returned_file_list  # Update file cue
            self.cued_file_count = len(self.cued_file_list)  # Update file count
            self.update_cue_count_lbl()  # Update file count label
            if self.cued_file_count == 0:  # If all files have been removed from cue, remove unavailable options
                self.run_analysis_btn['state'] = tk.DISABLED  # Disable run analysis button
                self.edit_files_btn['state'] = tk.DISABLED

    def update_cue_count_lbl(self):
        self.cued_file_count_lbl.config(text=str(self.cued_file_count) + " files cued")

    def quit_script(self):
        print("Leaving program")
        self.destroy()
        exit()


class EditCue(tk.Toplevel):
    """modal window requires a master"""
    def __init__(self, passed_file_list, master, **kwargs):
        super().__init__(master, **kwargs)

        self.saved_changes = None
        self.returned_file_list = None

        # x, y padding for tkinter objects
        pdx = 5
        pdy = 5

        # Create listbox for cued files
        cue_list = tk.Variable(value=passed_file_list)
        self.file_list_listbox = tk.Listbox(self, listvariable=cue_list, selectmode=EXTENDED, width=0, height=20)
        self.file_list_listbox.pack(padx=pdx, pady=pdy, expand=True, side=LEFT)
        self.file_list_listbox.bind('<<ListboxSelect>>', self.list_item_selected)

        # Add vertical scrollbar
        self.file_list_scrollbar = Scrollbar(self)
        self.file_list_scrollbar.pack(side=LEFT, fill=BOTH)
        self.file_list_listbox.config(yscrollcommand=self.file_list_scrollbar.set)
        self.file_list_scrollbar.config(command=self.file_list_listbox.yview)

        # Create frame for buttons
        edit_btn_frame = Frame(self)
        edit_btn_frame.pack(side=tk.RIGHT, anchor=NE)

        # Create a button to remove selected files
        self.remove_selected_btn = ttk.Button(
            edit_btn_frame,
            text="Remove selected",
            command=self.remove_selected_clicked,
            state=tk.DISABLED)  # Start with button disabled until files are selected
        self.remove_selected_btn.pack(padx=pdx, pady=pdy, side=TOP)

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
            text="Cancel",
            command=self.close_clicked)
        close_btn.pack(padx=pdx, pady=pdy, side=TOP)

        # The following commands keep the popup on top and stop clicking on the main window during editing
        self.transient(master)  # set to be on top of the main window
        self.grab_set()  # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self)  # pause anything on the main window until this one closes

    def list_item_selected(self, event):
        selected = event.widget.curselection()
        if len(selected) > 0:
            self.remove_selected_btn['state'] = tk.NORMAL
        else:
            self.remove_selected_btn['state'] = tk.DISABLED

    def close_clicked(self):
        self.saved_changes = False  # Flag no changes made
        self.destroy()

    def remove_selected_clicked(self):
        files_selected = self.file_list_listbox.curselection()
        for index in files_selected[::-1]:  # Start from last item selected so that indices aren't changed
            self.file_list_listbox.delete(index)
        self.save_changes_btn['state'] = tk.NORMAL  # Enable saving changes
        self.remove_selected_btn['state'] = tk.DISABLED  # Disable removing selected (they're already gone)

        # If all files are removed, add note of this to listbox and disable it
        if self.file_list_listbox.size() == 0:
            self.file_list_listbox.pack_forget()  # Hide the listbox
            # Create temporary label to replace listbox with
            temp_label = Label(self, text=">>> All files removed <<<", borderwidth=3, relief="groove", bg='white')
            temp_label.pack(ipadx=50, ipady=50, expand=True, side=LEFT)
            self.remove_selected_btn['state'] = tk.DISABLED  # Disable remove selected button
            self.file_list_scrollbar.pack_forget()  # Hide the scrollbar

    def save_changes_clicked(self):
        # Set cue list to only those values still in list box
        self.returned_file_list = self.file_list_listbox.get(0, END)  # Get all the files still in tuple
        self.saved_changes = True
        self.destroy()  # Close the window


class RunAnalysis(tk.Toplevel):
    """modal window requires a master"""
    def __init__(self, passed_file_list, file_import_settings, master, **kwargs):
        super().__init__(master, **kwargs)

        # x, y padding for tkinter objects
        pdx = 5
        pdy = 5

        # Create a temporary label - replace this with meaningful feedback
        temp_lbl = Label(self, text="Add feedback on progress here")
        temp_lbl.pack(padx=pdx, pady=pdy)

        # Create a button to close the window when analysis is complete
        close_btn = Button(self, text="Close", command=self.analysis_complete, state=tk.DISABLED)
        close_btn.pack(padx=pdx, pady=pdy)

        for file in passed_file_list:
            df = self.read_data_file(file, file_import_settings)

        close_btn['state'] = tk.NORMAL

        # The following commands keep the popup on top and stop clicking on the main window during editing
        self.transient(master)  # set to be on top of the main window
        self.grab_set()  # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self)  # pause anything on the main window until this one closes

    def read_data_file(self, file, import_settings):
        if os.path.exists(file):  # If the file exists
            df = pd.read_csv(
                file,
                sep=import_settings['delim'],
                skiprows=import_settings['skip'],
                dtype={'Time': float, 'Frame': int, 'X': float, 'Y': float},
                # converters={'Time': self.custom_data_converter},
                engine=import_settings['engine'],
                skipfooter=import_settings['skipfooter']
            )
            print(file, "\n", df.dtypes, "\nShape: ", df.shape, "\n", df.tail(10))
            if df is pd.DataFrame:
                return df
            else:
                return "Could not read file"
        else:
            return "File not found"

    # def custom_data_converter(self, val):
    #     try:
    #         return float(val)
    #     except:
    #         return "#N/A"

    def analysis_complete(self):
        # Blows up with destroy if called directly from __init__ but not from a button command. Need to figure out why
        self.destroy()  # Finished with window, close it


def main():
    # Get data file definitions
    data_file_definitions = get_file_definitions(11)  # Read in data file specifications (number of expected columns)
    if type(data_file_definitions) is pd.DataFrame:  # If script has returned a df rather than error code (integer)
        # create root window.
        root = tk.Tk()
        root.title("Bulk file analyser")
        window = BuildCue(data_file_definitions, root)
        window.pack()
        root.mainloop()
    else:
        exit()


if __name__ == '__main__':
    main()

# Function used for testing function calls in JSON_play. Can be deleted after finished testing
def test_func(vars):
    print("test_func in bulk file called")