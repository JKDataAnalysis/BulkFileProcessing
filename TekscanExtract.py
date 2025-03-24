import os

"""
This function has now been moved to AnalysisTemplate_Tekscan
"""


def tekscan_extract(f, search_name='', overwrite=False, **kwargs):
    """
    There is a problem with the file exporting from Tekscan Footscan in that, if more than one windows are open when a
    file is export, then all open files will be included in the export. One of the issues that this creates is that if
    the data is read in from the file, then the second and later data sets headers will be read in as data leading to
    data type errors and also meaning data from different data sets could be merged. This function remedies that by
    extracting data sets from the passed file and saving these to a backup folder or overwriting the original.

    :param f: path to file to read from
    :param search_name: The filename to search for in lines in the file starting 'FILENAME'. If this is not, set then
    the base name of the file passed will be used.
    :param overwrite: What to do with the copies of files. If False (default): move the source file to a directory named
    'backup' in the source file directory. True: overwrite the original file.
    :return: The path to the new file (or original filepath if no changes required) or an error message
    """
    # No search name passed, use source filename
    if not search_name:
        # Extract just the filename from the file path
        search_name = os.path.splitext(os.path.basename(f))[0]

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
        if search_name in matching_lines[0][1]:  # Only filename in file header matches search name
            return f  # Doesn't need extraction-return original filename
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
        if match_file[0][0] == len(matching_lines) - 1:  # -1 since len gives count but array indexing is 0:
            end_line = len(fl_lines)  # Set last line to read as the end of the file
        else:
            end_line = matching_lines[match_file[0][0]+1][0]

        # Pad start of block with file header lines
        block = fl_lines[0:4] + fl_lines[start_line:end_line]

        source_dir = os.path.dirname(f)  # Get source directory
        source_file = os.path.splitext(os.path.basename(f))  # Get source filename and filetype extension

        # Backup the original file
        if not overwrite:  # Unless set to overwrite
            backup_dir = os.path.join(source_dir, 'backup')  # Append 'backup' to source directory
            if not os.path.exists(backup_dir):  # backup directory doesn't already exist
                os.makedirs(backup_dir)  # Create it
            backup_file = os.path.join(backup_dir, source_file[0] + source_file[1])
            # If there's already a file with that name, append a number
            cnt = 0
            while os.path.exists(backup_file):
                cnt += 1
                backup_file = os.path.join(backup_dir, source_file[0]) + '_' + str(cnt) + source_file[1]
            try:
                os.rename(f, backup_file)  # Move source file to backup folder
            except Exception as e:
                return 'Unable to backup source file:' + f + ':', e

        # Write extracted data back to the original file name (or search name)
        target_filename = os.path.join(source_dir, search_name) + source_file[1]
        cnt = 0
        # Check file doesn't already exist. This would only happen if a search name is passed and it matched a file
        # already existing in the source file directory
        while os.path.exists(target_filename):
            cnt += 1
            target_filename = os.path.join(source_dir, search_name) + '_' + str(cnt) + source_file[1]

        try:
            with open(target_filename, "w") as fl:
                fl.writelines(block)  # Write block to file
        except Exception as e:
            os.rename(backup_file, f)  # Restore source file from backup folder
            return 'Unable to save file as:' + target_filename + ': ' + repr(e)
        else:
            return target_filename


if __name__ == '__main__':
    """
    """

    # file = '/home/jon/Documents/TestData/RecentData/BakeE04.csv'
    # file = '/home/jon/Documents/TestData/RecentData/BeatA02.csv'
    file = '/home/jon/Documents/TestData/RecentData/CARTN25.csv'
    # file = '/home/jon/Documents/TestData/RecentData/CleanedFiles/CARTN22_1.csv'
    extracted_file = tekscan_extract(file, search_name='CARTN28')
    if os.path.exists(os.path.dirname(extracted_file)):
        result = 'File'
    else:
        result = 'Error'
    print(result, ':', extracted_file)