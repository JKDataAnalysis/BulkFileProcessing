"""
TODO
    =====
    Major
    =====
    * Create window to run analysis- just show progress bar and label
        - Once complete show options for results- save as / view
    --- Start of loop
        * Read in first file
        * Process data in first file
        * Add results of processing to results df
    --- End of loop
    * Write results df to file
    =====
    Minor
    =====
    * The width of the listbox in EditCue is set to a fixed value. This will stop it from shrinking to a really small
     size if all files are removed but path lengths could be longer than this. Think of a better way to handle this.
    * padx and pady values are currently set within the classes rather than being passed to them
    * Vertical scroll bar on edit files listbox should only display if the number of files displayed is greater than the
     listbox height
    ==========
    Known bugs
    ==========
    * BuildCue.edit_cue also giving 'method may be static' error as .self never used
    * See also Problems
"""
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import ttk

import pandas as pd
import os
import sys
from tkinter import *


def get_file_definitions(def_cols):
    # Set file to default location and name
    data_def_file = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "DataFileSpec.csv")
    if os.path.exists(data_def_file):  # If the default file exists
        arr = pd.read_csv(data_def_file, delimiter=",")  # Read it into a df
        if arr.shape[0] >= 1 and arr.shape[1] == def_cols:  # Check at least 1 source type and correct number of columns read
            return arr
        else:
            messagebox.showerror(
                title="Failed to read data file definitions",
                message="Aborting: Error in data file definitions found",
                detail=f"Expected at least 1 row of {def_cols} columns\nGot {arr.shape[0]} rows of {arr.shape[1]}",
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
            text="Add files",
            command=self.add_files_btn_clicked)
        self.add_files_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT, anchor=tk.NW)

        # create button to view/ edit file cue
        self.edit_files_btn = ttk.Button(
            build_cue_btn_frm,
            text="View/ edit cue",
            command=self.edit_cue_clicked)
        self.edit_files_btn.pack(side=tk.LEFT, padx=pdx, pady=pdy)

        # Create label of files in cue
        cued_file_count = 0
        self.cued_file_count_lbl = Label(data_files_lblfrm)
        self.cued_file_count_lbl.pack(padx=pdx, pady=pdy, side=tk.BOTTOM, anchor=tk.NW)
        self.update_cue_count_lbl()

        main_btn_frame = tk.Frame(self, borderwidth=5, relief=tk.RAISED, bg='red', width=500)
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
        quit_btn = ttk.Button(main_btn_frame, text="Quit", command=self.quit_script)
        quit_btn.pack(padx=pdx, pady=pdy, side=tk.LEFT)

        # Set window to initial conditions
        self.reset_window()

    def source_type_selected(self, event):
        event.widget['state'] = tk.DISABLED  # Disable changing file type
        self.add_files_btn['state'] = tk.NORMAL

    def add_files_btn_clicked(self):
        # Get the source file type selected in the combo box
        selected_source_type = self.source_type_combo.get()

        # Get the import settings for the selected source file type
        self.file_import_settings = self.data_file_defs.loc[self.data_file_defs['source'] == selected_source_type]
        # Flatten to a pandas series
        self.file_import_settings = self.file_import_settings.squeeze()

        # Extract the matching file type and file type label
        file_type = self.file_import_settings['file_type']
        file_type_label = self.file_import_settings['file_type_label']
        self.add_files(file_type, file_type_label)

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

        # x, y padding for tkinter objects
        pdx = 5
        pdy = 5

        # Create listbox for cued files
        cue_list = tk.Variable(value=passed_file_list)
        self.file_list_listbox = tk.Listbox(self, listvariable=cue_list, selectmode=EXTENDED, width=80, height = 20)
        self.file_list_listbox.pack(padx=pdx, pady=pdy, expand=True, side=LEFT)
        # Add vertical scrollbar
        file_list_scrollbar = Scrollbar(self)
        file_list_scrollbar.pack(side=LEFT, fill=BOTH)
        self.file_list_listbox.config(yscrollcommand=file_list_scrollbar.set)
        file_list_scrollbar.config(command=self.file_list_listbox.yview)

        # Create frame for buttons
        edit_btn_frame = Frame(self)
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
            command=self.close_clicked)
        close_btn.pack(padx=pdx, pady=pdy, side=TOP)

        # The following commands keep the popup on top and stop clicking on the main window during editing
        self.transient(master)  # set to be on top of the main window
        self.grab_set()  # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self)  # pause anything on the main window until this one closes

    def close_clicked(self):
        self.saved_changes = False  # Flag no changes made
        self.destroy()

    def remove_selected_clicked(self):
        files_selected = self.file_list_listbox.curselection()
        selected_count = len(files_selected)
        if selected_count == 0:
            messagebox.showinfo(title="no selection", message="No files selected")
        else:
            for item in files_selected:
                self.file_list_listbox.delete('active')
            self.save_changes_btn['state'] = tk.NORMAL
            # if self.file_list_listbox.size() == 0: # No items left
            #     self.file_list_listbox.config['width'] = 20

    def save_changes_clicked(self):
        # Set cue list to only those values still in list box
        self.returned_file_list = self.file_list_listbox.get(0, END)  # Get all the files still in tuple
        self.saved_changes = True
        self.destroy()  # Close the window


def main():

    # Get data file definitions
    data_file_definitions = get_file_definitions(8)  # Read in data file specifications
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