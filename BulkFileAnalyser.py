"""
TODO
    ==========
    Known bugs
    ==========
    * Frames within main window do not expand if the window is expanded (probably should disable resizing for other
    windows)
    ====
    NEXT
    ====
    * The function checking routines will not find a module even if it is imported into the calling script. Is that
    an OK behaviour?
    * Move functions not directly related to the tkinter classes out of classes
        - BuildCue - check import profile funcs
        - EditCue - OK
        - RunAnalysis -  Only contains __init__
    * Add notes to rest of functions
        - DONE: BuildCue class
        - To do: EditCue class
        - To do: RunAnalysis class
        - DONE: none class functions
    * Work on making it all more OOP.
    * Look at raising custom errors at least for fatal errors :
     https://www.geeksforgeeks.org/define-custom-exceptions-in-python/
    * Implement reading information from headers (e.g. sample rate, recording date)
        - DONE: write function
        - DONE: Potential information added to JSON
        - TO DO: Add to required keys list
        - TO DO: Update information on Git
        * Write file as text if write to csv fails
    * Add some example analyses: Need to think about how to handle this. Should analyses be fixed for analysis types
    (e.g. balance for Tekscan or balance or jump for Bioware?) or should this be separate?
    =====
    Later
    =====
    * Are there other ways to flag potential read errors (other than column types as object)?
    * padx and pady values are currently set within the classes rather than being passed to them
        - Look at creating a style and setting to widgets
    * Vertical scroll bar on edit files listbox should only display if the number of files displayed is greater than the
     listbox height
    * default_dir to start looking for data files is temporarily set to location of tekscan test data. This should be
    the last used folder
    ==========
    Much later
    ==========
"""

import tkinter as tk
from json import JSONDecodeError
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import ttk

import pandas as pd
import os
import sys
from tkinter import *
import glob
import json
import importlib


def get_analysis_profiles():
    """
    Load the analysis profile from JSON file
    :return: Dictionary of analysis profile or error message
    """
    # Set file to default location and name
    analysis_profiles_file = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "DataFileImportSettings.json")
    if os.path.exists(analysis_profiles_file):  # If the default file exists
        with open(analysis_profiles_file, "r") as fp:
            try:
                data_file_defs = json.load(fp)
            except JSONDecodeError:
                return ('error', {
                    'message': 'Aborting: Reading JSON format information from analysis profile file failed',
                    'detail': 'Search path:\n' + analysis_profiles_file
                })
            except Exception as e:
                print(repr(e))
                return ('error', {
                    'message': 'Aborting: Unhandled error reading JSON format information from analysis profile file',
                    'detail': 'Search path:\n' + analysis_profiles_file
                })
        if isinstance(data_file_defs, dict):  # If have successfully read in dictionary
            if len(list(data_file_defs.keys())) >= 1:  # If there is at least one defined type
                return data_file_defs
            else:
                return ('error', {
                    'message': 'Aborting: No analysis definitions found in file',
                    'detail': 'Search path:\n' + analysis_profiles_file
                })
        else:
            return ('error', {
                'message': 'Aborting: Error reading analysis definitions',
                'detail': 'Search path:\n' + analysis_profiles_file
            })
    else:
        return ('error', {
            'message': 'Aborting: No analysis definitions file found',
            'detail': 'Search path:\n' + analysis_profiles_file
        })


class BuildCue(tk.Frame):
    """
    Tkinter Frame to select analysis profile type, add files to cue and trigger analysis
    """
    def __init__(self, data_file_definitions, master=None, **kwargs):
        """

        :param data_file_definitions: Dictionary of data file definitions
        :param master:
        :param kwargs: Any other keywords
        """
        super().__init__(master, **kwargs)
        self.file_import_settings = None
        self.cued_file_list = None
        self.cued_file_count = 0  # Reset file counter
        self.data_file_defs = data_file_definitions
        self.file_handling_funcs = {}  # Dictionary of file handling functions and keys as labels

        # x, y padding for tkinter objects
        pdx = 5
        pdy = 5

        # create choose analysis type label
        self.choose_data_analysis_type_lblfrm = LabelFrame(self, text="Analysis type profile")
        self.choose_data_analysis_type_lblfrm.pack(padx=pdx, pady=pdy, side=tk.TOP, anchor=tk.NW, fill='x', expand=True)

        # create combobox object to select analysis type
        defined_analyses = tk.StringVar()
        self.analysis_type_combo = ttk.Combobox(
            self.choose_data_analysis_type_lblfrm,
            textvariable=defined_analyses,
            state='readonly')
        self.analysis_type_combo['values'] = list(self.data_file_defs.keys())
        self.analysis_type_combo.set("Choose analysis type")
        self.analysis_type_combo.pack(padx=pdx, pady=pdy, side=tk.LEFT, anchor=tk.NW, fill='x', expand=True)
        self.analysis_type_combo.bind('<<ComboboxSelected>>', self.analysis_type_selected)

        # create button to add import profile
        self.add_files_btn = ttk.Button(
            self.choose_data_analysis_type_lblfrm,
            text="Add import profile",
            state=tk.DISABLED)
        self.add_files_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT, anchor=tk.NE)

        # Create a frame for file cue widgets
        data_files_lblfrm = LabelFrame(self, text="File cue")
        data_files_lblfrm.pack(padx=pdx, pady=pdy, side=tk.TOP, anchor=tk.NW, fill='x', expand=True)

        # Create a frame for build cue buttons and subfolder checkbox
        build_cue_btn_frm = Frame(data_files_lblfrm)
        build_cue_btn_frm.pack(padx=pdx, pady=pdy, side=tk.TOP, anchor=tk.NW, fill='x', expand=True)

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
        self.add_folder_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT, anchor=tk.NW)

        # Create checkbox to include subfolders
        self.include_subdirs = tk.BooleanVar()
        self.include_subdir_chk = ttk.Checkbutton(
            build_cue_btn_frm,
            text="Include\nsubfolders",
            variable=self.include_subdirs)
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

        # Create a frame for the main buttons (quit, reset, run analysis)
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

    def check_import_profile(self, selected_import_settings):
        """
        Check that the selected import profile contains all of the required keys and that the functions listed are valid
        :param selected_import_settings: Dictionary of import settings to check
        :return: Dictionary of function objects or an error message
        """
        # Dictionary of keys that selected import settings must contain to be valid
        required_keys_list = {
            "file_type": ["type", "label"],
            "clean_file_func": ["module", "func", "parameters"],
            "read_file_func": ["module", "func", "parameters"],
            "analysis_func": ["module", "func", "parameters"],
            "read_header_func": ["module", "func", "parameters", "headers"],
        }

        # Check selected dictionary against required keys
        key_error = self.check_import_setting_keys(selected_import_settings, required_keys_list)
        if key_error:
            return "Key error: " + key_error

        # Filter dictionary keys for only those that end in '_func'
        func_dict = {k: v for k, v in selected_import_settings.items() if k.endswith('_func')}
        return self.check_build_func(func_dict)

        # # Functions can now be called by filtering the dictionary for the required key/ value pair as:
        # self.file_handling_funcs['read_file_func']()
        # self.file_handling_funcs['analysis_func']()

    def analysis_type_selected(self, event):
        """
        Callback for when an analysis type is selected in the combobox
        :param event: event object from TkInter widget
        :return: None
        """
        # Get the analysis type selected in the combo box
        selected_analysis_type = self.analysis_type_combo.get()

        # Get the import settings for the selected analysis type
        self.file_import_settings = self.data_file_defs[selected_analysis_type]

        functions = self.check_import_profile(self.file_import_settings)
        if not isinstance(functions, dict):  # Did not successfully return functions
            messagebox.showerror(
                title="Analysis type profile error",
                message="Error in selected analysis type specifications\nAnalysis type will be disabled",
                detail=functions,
                icon='error')

            tmp_list = list(self.analysis_type_combo['values'])  # Convert to list so can edit
            tmp_list.remove(selected_analysis_type)  # Remove selected item
            self.analysis_type_combo['values'] = tuple(tmp_list)  # Convert back to tuple and reassign
            self.analysis_type_combo.set('')  # Clear selection
            if len(self.analysis_type_combo['values']) == 0:  # If no options left
                messagebox.showerror(
                    title="No valid analysis profiles",
                    message="There are no valid analysis profiles available\nUnable to continue",
                    icon='error')
                self.quit_script()
        else:  # All ok, enable next steps
            event.widget['state'] = tk.DISABLED  # Disable changing file type
            # Enable adding files/ folders and whether subfolders are to be included
            self.add_files_btn['state'] = tk.NORMAL
            self.add_folder_btn['state'] = tk.NORMAL
            self.include_subdir_chk['state'] = tk.NORMAL
            self.file_handling_funcs = functions

    def add_files_btns_clicked(self, file_folder):
        """
        Callback for when either 'Add files' or 'Add folder' button is clicked
        :param file_folder: flag for whether 'Add files' ('files') or 'Add folder' ('folder' button was clicked
        :return: None
        """
        if file_folder == "files":  # Add files button clicked
            self.add_files(
                self.file_import_settings["file_type"]["type"],
                self.file_import_settings["file_type"]["label"])
        elif file_folder == "folder":  # Add folders button clicked
            self.add_folder(self.file_import_settings["file_type"]["type"])
        else:  # How the hell did we get here?
            messagebox.showerror(
                title="Button callback function error",
                message="Function called by file button is not recognised")
            self.quit_script()

    def check_import_setting_keys(self, dict_to_check, check_list):
        """
        check that the dictionary contains all the keys in the check-list
        :param dict_to_check: dictionary to check
        :param check_list: Keys that the dictionary should be checked for (also as dict)
        :return: False if there are no errors with any of the keys, i.e. all found or an error message string on the
         first key not found
        """
        # Check first level keys
        k = check_dict_keys(dict_to_check.keys(), check_list.keys())
        if k:  # Errors found in first level keys
            return f"First level: key '{k}' not found"

        # Check second level keys
        for sub_key in check_list:
            sub_dict = dict_to_check[sub_key].keys()
            check_sub_keys = check_list[sub_key]
            if len(check_sub_keys) > 0:  # Don't check subkeys if there aren't any
                if check_dict_keys(sub_dict, check_sub_keys):
                    return f"Second level: key '{sub_key}' not found"  # Errors found in second level keys
        return False  # No errors found

    def check_build_func(self, func_dict):
        """
        Build a dictionary object of function objects after having first checked that they are all valid
        :param func_dict: Dictionary of modules and functions {"module":value, "func": value}.
        :return: dictionary of function objects or error message string
        """
        functions = {}
        for d in func_dict:
            # Check function unless it's the clean_file_func (optional) AND there is no value set for func
            if d == "clean_file_func" and not func_dict[d]['func']:  # Empty string will return as True
                functions[d] = None
            else:
                r = check_functions(func_dict[d])
                if isinstance(r, str):  # If returned an error message
                    return d + ': ' + r
                else:
                    functions[d] = r
        return functions

    def add_files_to_cue(self, file_list):
        """
        Add passed file list to cue and update the file count and enable buttons for next stage
        :param file_list: List of files to add (list)
        :return: None
        """
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
        """
        Allow user to select file(s) to be added to the cue
        :param file_type: file type to filter displayed files by
        :param file_type_label: Label to use in the 'file type' combobox in the askopenfilenames dialogue box
        :return: tuple of chosen files
        """
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

    def add_folder(self, file_type):
        """
        Allow user to select folder from which all files matching file_type will be added to the cue
        :param file_type: file type to filter files by
        :return: tuple of chosen files
        """
        default_dir = '/home/jon/Documents/TestData/RecentData'
        selected_folder = fd.askdirectory(
            title='Open files',
            initialdir=default_dir,
            mustexist=True
        )
        if not os.path.isdir(selected_folder):  # Will be unless user clicked cancel
            return

        file_list = list(self.cued_file_list)  # Start with existing tuple of files (as list)

        # If including subdirectories, add this
        if self.include_subdirs.get():
            add_subs = "**"
        else:
            add_subs = ""
        # Combine chosen folder path with wildcard and passed file type
        file_filter = os.path.join(selected_folder, add_subs, "*." + file_type)
        files = glob.glob(file_filter, recursive=self.include_subdirs.get())  # Get list of matching files and folders
        for f in files:  # Add only files (not directories)
            if os.path.isfile(f):
                file_list.append(f)
        self.add_files_to_cue(tuple(file_list))  # As tuple to match what add files will produce

    def run_analysis_clicked(self):
        """
        Callback for when 'Run analysis' button is clicked. Opens RunAnalysis top level frame. Optionally clears file
        cue when RunAnalysis frame is closed
        :return: None
        """
        RunAnalysis(
            self.cued_file_list,
            self.file_import_settings,
            self.file_handling_funcs,
            self)
        ans = messagebox.askyesno(
            title='Clear file cue',
            message='Clear files from cue?')
        if ans:
            self.cued_file_list = tuple()  # Clear the file cue
            self.cued_file_count = 0  # Reset file counter
            self.update_cue_count_lbl()  # Update the displayed value
            self.edit_files_btn['state'] = tk.DISABLED  # Disable view/ edit file cue button
            self.run_analysis_btn['state'] = tk.DISABLED  # Disable run analysis button

    def reset_window(self):
        """
        Set items in BuildCue tk.Frame to their initial state.
        :return: None
        """
        self.cued_file_list = tuple()  # Clear the file cue
        self.cued_file_count = 0  # Reset file counter
        self.update_cue_count_lbl()  # Update the displayed value
        self.analysis_type_combo['state'] = tk.NORMAL  # Reactivate file type combo box
        self.analysis_type_combo.set('')  # Remove any selection
        self.add_files_btn['state'] = tk.DISABLED  # Disable add files button
        self.add_folder_btn['state'] = tk.DISABLED  # Disable add folder button
        self.include_subdir_chk['state'] = tk.DISABLED  # Disable include subfolders checkbox
        self.edit_files_btn['state'] = tk.DISABLED  # Disable view/ edit file cue button
        self.run_analysis_btn['state'] = tk.DISABLED  # Disable run analysis button

    def edit_cue_clicked(self):
        """
        Callback for when 'Edit Cue' button is clicked. Opens EditCue top level frame. When EditCue frame is closed
        updates the file cue information.
        :return: None
        """
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
        """
        Updates the cue count label
        :return: None
        """
        self.cued_file_count_lbl.config(text=str(self.cued_file_count) + " files cued")

    def quit_script(self):
        """"
        Closes BuildCue tk.frame and exits script
        """
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

        # Create a button to select all files
        self.select_all_btn = ttk.Button(
            edit_btn_frame,
            text="Selected all",
            command=self.select_all_clicked)
        self.select_all_btn.pack(padx=pdx, pady=pdy, side=TOP, fill=X)

        # Create a button to remove selected files
        self.remove_selected_btn = ttk.Button(
            edit_btn_frame,
            text="Remove selected",
            command=self.remove_selected_clicked,
            state=tk.DISABLED)  # Start with button disabled until files are selected
        self.remove_selected_btn.pack(padx=pdx, pady=pdy, side=TOP, fill=X)

        # Create a button to save changes to list
        self.save_changes_btn = ttk.Button(
            edit_btn_frame,
            text="Save changes",
            command=self.save_changes_clicked,
            state=tk.DISABLED)
        self.save_changes_btn.pack(padx=pdx, pady=pdy, side=TOP, fill=X)

        # Create a button to close (destroy) this window.
        close_btn = ttk.Button(
            edit_btn_frame,
            text="Cancel",
            command=self.close_clicked)
        close_btn.pack(padx=pdx, pady=pdy, side=TOP, fill=X)

        # The following commands keep the popup on top and stop clicking on the main window during editing
        self.transient(master)  # set to be on top of the main window
        self.grab_set()  # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self)  # pause anything on the main window until this one closes

    def select_all_clicked(self):
        self.file_list_listbox.select_set(0, END)
        self.remove_selected_btn['state'] = tk.NORMAL

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


def read_text_file(file, import_settings):
    """
    :param file: File path of file to read in
    :param import_settings: any parameters to pass into the read function (Pandas.read_csv)
    :return: a tuple containing the dataframe read in and a string indicating read status ('OK' if read successfully)
    """
    if os.path.exists(file):  # If the file exists
        try:
            df = pd.read_csv(
                file,
                **import_settings)
        except Exception as e:
            print('Error reading:', file, '/nError details:', repr(e))
            return "", 'FAIL: ' + type(e).__name__  # df, error message to write to file
        else:  # Read OK
            if object in list(df.dtypes):
                return df, "CHECK: Possible errors"  # df, error message to write to file
            else:
                return df, "OK"
    else:
        return "", "File not found"


def read_header():
    pass


def save_df_to_file(df, dflt_ext='.csv', incl_index=False, confirm_overwrite=True):
    """
    Saves the passed Pandas Dataframe to a csv file. The user is asked for the file to save to.
    :param df: The Pandas dataframe to be written
    :param dflt_ext: The filetype extension that will be appended to the file if none is set by the user
    :param incl_index: Whether to include the index column of the dataframe in the export
    :param confirm_overwrite: Whether overwriting should be confirmed if the file already exists
    :return:
    """
    saved_file = False
    while not saved_file:
        filename = fd.asksaveasfilename(confirmoverwrite=confirm_overwrite, defaultextension=dflt_ext)
        if filename:  # Will evaluate as True if a filename is returned
            try:
                df.to_csv(filename, index=incl_index)
            except UnicodeError as e:
                messagebox.showerror(
                    Title='Error saving file',
                    message='The results DataFrame contains characters that cannot be encoded in the default encoding',
                    detail=e)
            except ValueError as e:
                messagebox.showerror(
                    Title='Error saving file',
                    message='Value error. This can arise if the results Dataframe contains separator characters or ' +
                            'very large integers.',
                    detail=e)
            except MemoryError as e:
                messagebox.showerror(
                    Title='Error saving file',
                    message='Memory error. This can arise if the results Dataframe ' +
                            'is too large to fit into available memory during the saving process.',
                    detail=e)
            except Exception as e:
                messagebox.showerror(
                    Title='Error saving file',
                    message='Unhandled error.',
                    detail=e)
            else:
                print('Results file saved to:', filename)
            saved_file = True
        else:  # Will evaluate as False if the string is empty (user clicked Cancel)
            ans = messagebox.askretrycancel(
                title="Results not saved",
                message="Results are not saved\nCancel saving?",
                icon='warning')
            if not ans:  # User clicked Cancel
                saved_file = True


class RunAnalysis(tk.Toplevel):
    """modal window requires a master"""

    def __init__(self, passed_file_list, file_import_settings, file_handling_funcs, master, **kwargs):
        super().__init__(master, **kwargs)

        self.file_handling_funcs = file_handling_funcs

        # x, y padding for tkinter objects
        pdx = 5
        pdy = 5

        # Create a temporary label - replace this with meaningful feedback
        temp_lbl = Label(self, text="Add feedback on progress here")
        temp_lbl.pack(padx=pdx, pady=pdy)

        # Create a button to close the window when analysis is complete
        close_btn = Button(self, text="Close", command=self.analysis_complete, state=tk.DISABLED)
        close_btn.pack(padx=pdx, pady=pdy)

        # Iterate through each file in cue and process
        all_results_list = []  # Create empty list for storing list of dicts of all results
        # if not self.file_handling_funcs['clean_file_func'] == None:  # If a function is given in JSON file rather than ""
        clean_file_function = self.file_handling_funcs['clean_file_func']
        clean_file_parameters = file_import_settings['clean_file_func']['parameters']
        read_file_function = self.file_handling_funcs['read_file_func']
        read_file_parameters = file_import_settings["read_file_func"]["parameters"]
        for file in passed_file_list:

            # clean_file_function is read from JSON file so won't exist in script
            if clean_file_function is not None:  # If a function is given in JSON file rather than ""
                clean_file_function(file, clean_file_parameters)

            # read_file_function is read from JSON file so won't exist in script
            data_df, read_status = read_file_function(file, read_file_parameters)
            file_results_dict = {
                "Filename": os.path.splitext(os.path.basename(file))[0],
                "Path": os.path.dirname(file),
                "Read status": read_status
            }
            if isinstance(data_df, pd.DataFrame):  # If successfully read in data
                read_success_dict = {
                    "Rows": data_df.shape[0],
                    "Columns": data_df.shape[1]
                    }
            else:
                read_success_dict = {
                    "Rows": 0,
                    "Columns": 0
                    }
            file_results_dict.update(read_success_dict)

            all_results_list.append(file_results_dict)  # Add results from file to list of dicts
        results_df = pd.DataFrame(all_results_list)  # Convert list to df
        save_df_to_file(results_df)
        self.analysis_complete()
        # analysis_complete destroys this window so this prevents errors when it hits lines below
        # Its included with an if statement so that the lines below don't report as being unreachable
        # In theory, a situation could arise where the window fails to close and then it would hit the last lines and
        # reach an error state
        if self.winfo_exists():
            # The following commands keep the popup on top and stop clicking on the main window during editing
            self.transient(master)  # set to be on top of the main window
            self.grab_set()  # hijack all commands from the master (clicks on the main window are ignored)
            master.wait_window(self)  # pause anything on the main window until this one closes

    def analysis_complete(self):
        # Blows up with destroy if called directly from __init__ but not from a button command. Need to figure out why
        self.destroy()  # Finished with window, close it


# Should be outwith class
def check_dict_keys(d, key_check_dict):
    """
    :param d: The dictionary to check
    :param key_check_dict: A dictionary of keys to search the dictionary for
    :return: False if all keys are found or the value of the first key not found
    """
    for key in key_check_dict:
        if key not in d:
            return key  # Return key not found
    return False  # No missing keys found


def check_functions(func_to_check):
    """
    Check whether function is valid
    :param func_to_check: dictionary {'module', 'func'}
    :return: function object or error string
    """
    module = func_to_check['module']
    func = func_to_check['func']

    if not module:  # Blank string: function is within calling script
        if func in globals():
            if callable(eval(func)):  # Check that the object is callable, i.e. a function
                return eval(func)
            else:
                return f"Object '{func}' found in calling script but it is not callable"
        else:
            return f"Function '{func}' not found in calling script"
    else:
        if module in sys.modules:  # Check if module is already in imports
            module = sys.modules[module]
            if hasattr(module, func):  # Check if object exists within the module
                if callable(getattr(module, func, None)):  # Check that the object is callable, i.e. a function
                    return getattr(module, func, None)
                else:
                    return f"Object '{func}' found in module '{func_to_check['module']}' but it is not callable"
            else:
                return f"Module '{module}' found but not function '{func}'"
        else:  # Try to import module
            if os.path.isfile(module):  # If module is a file path
                module_path = os.path.dirname(module)  # Get path to file
                module = os.path.splitext(os.path.basename(module))[0]  # Get name of module
                sys.path.insert(0, module_path)  # Add the path to the working directory
            module = importlib.import_module(module, package=None)
            if hasattr(module, func):  # Check if object exists within the module
                if callable(getattr(module, func, None)):  # Check that the object is callable, i.e. a function
                    return getattr(module, func, None)
                else:
                    return f"Object '{func}' found in LOADED module '{func_to_check['module']}' but it is not callable"
            else:
                return f"Module '{module}' LOADED but function '{func}' not found"


def temp_analysis_func():
    # This is just here to give the import profiles something to point at until there's a proper target
    pass


def main():
    # Get analysis definitions
    data_file_definitions = get_analysis_profiles()  # Read in analysis specifications
    if isinstance(data_file_definitions,
                  dict):  # If script has returned a dict rather than an error (returned as tuple)
        # create root window.
        root = tk.Tk()
        root.title("Bulk file analyser")
        window = BuildCue(data_file_definitions, root)
        window.pack()
        root.mainloop()
    else:
        messagebox.showerror(
            title="Failed to read analysis definitions",
            icon='error',
            **data_file_definitions[1])
        exit()


if __name__ == '__main__':
    main()