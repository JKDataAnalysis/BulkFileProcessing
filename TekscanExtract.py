"""
There is a problem with the file exporting from Tekscan Footscan in that, if more than one windows are open when a file
is export, then all open files will be included in the export. One of the issues that this creates is that if the data
is read in from the file, then the second and later data sets headers will be read in as data leading to read errors and
also meaning data from different data sets could be merged.
This program remedies that by extracting data sets from the passed file and saving these or overwriting the orginial
"""
import os


def tekscan_extract(f, search_name='', dest_folder='', overwrite=False):
    """
    :param f: filepath to read from
    :param search_name: The filename to search for in lines in the file starting 'FILENAME'. If this is not, set then
    the base name of the file passed will be used.
    :param overwrite: [TO IMPLEMENT] Whether to overwrite the original file. If a destination folder is set, this
    parameter will be ignored
    than one data set were found. 'move' will move the original source files to a folder named 'ori
    :param dest_folder: [TO IMPLEMENT] where extracted file will be saved to. If this is not set then the file will be
    saved to a folder in the original file's folder named 'CleanedFiles'. If the folder does not exist, it will be
    created.
    :return: filepath to cleaned file or original file path if only one data set in the file and the filename in the
    header matches search_name or an error message
    """
# No search name passed, use source filename
    if not search_name:
        # Extract just the filename from the file path
        search_name = os.path.splitext(os.path.basename(f))[0]

    # Check if there's a valid destination directory to save to
    if dest_folder:  # No destination directory passed, create a folder in the source files folder if one doesn't exist
        if not os.path.exists(dest_folder):  # Passed destination folder does not exist
            return 'Destination folder does not exist', dest_folder
    else:
        dest_folder = os.path.join(os.path.dirname(f), 'CleanedFiles')
        overwrite = False  # If a destination folder is passed, ignore the overwrite option
        if not os.path.exists(dest_folder):  # If 'CleanedFiles' folder doesn't already exist, create it
            os.makedirs(dest_folder)

    try:
        with open(f, "r") as fl:
            fl_lines = fl.readlines()  # Read in whole file as lines of text
    except Exception as e:
        return 'Unable to read file: ' + f + ': ' + repr(e)
    else:
        # Filter lines to only those starting with filename and return an enumerated list
        matching_lines = [(i, x) for i, x in enumerate(fl_lines) if x.startswith('FILENAME')]

    # Only 1 data set found in file
    if len(matching_lines) == 1:
        if search_name in matching_lines[0][1]:
            return f  # Return the original filepath
        else:
            return search_name + ' not found in ' + f

    # Filter items in the matching_lines list that match the search filename
    # .find returns -1 if the item is not found or the firs occurrence if it is found. This therefore filters by
    # not not found!
    match_file = [(i, x) for i, x in enumerate(matching_lines) if not x[1].find(search_name) == -1]

    if len(match_file) > 1:  # If found more than one occurrence of the search name in the file
        return 'More than one occurrence of the search name (' + search_name + ' found in file: ' + f
    else:
        # Set start line
        start_line = matching_lines[match_file[0][0]][0]

        # If the item matching the search filename is the last in the list of filenames
        if match_file[0][0] == len(matching_lines):
            end_line = len(fl_lines)  # Set last line to read as the end of the file
        else:
            end_line = matching_lines[match_file[0][0]+1][0]

        # Pad start of block with file header lines
        block = fl_lines[0:4] + fl_lines[start_line:end_line]

        target_filepath = os.path.join(dest_folder, search_name)
        source_file_extension = os.path.splitext(os.path.basename(f))[1]
        target_file = target_filepath + source_file_extension
        if not overwrite:
            # If there's already a file with that name, append a number
            cnt = 0
            while os.path.exists(target_file):
                cnt += 1
                target_file = target_filepath + '_' + str(cnt) + source_file_extension

        try:
            with open(target_file, "w") as fl:
                fl.writelines(block)  # Write block to file
        except Exception as e:
            return 'Unable to save file as:' + target_file + ': ' + repr(e)
        else:
            return target_file

if __name__ == '__main__':
    # file = '/home/jon/Documents/TestData/RecentData/BakeE04.csv'
    file = '/home/jon/Documents/TestData/RecentData/BeatA02.csv'
    # file = '/home/jon/Documents/TestData/RecentData/CARTN22.csv'
    # file = '/home/jon/Documents/TestData/RecentData/CleanedFiles/CARTN22_1.csv'
    res_fl = tekscan_extract(file)
    if os.path.exists(os.path.dirname(res_fl)):
        if res_fl == file:
            print('Source and destination files are the same')
        else:
            print('New file written to: ', res_fl)
    else:
        print(res_fl)
