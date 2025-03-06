import BulkFileAnalyser
import os
import pandas as pd


def read_text_file_AT(file, import_settings):
    if os.path.exists(file):  # If the file exists
        df = pd.read_csv(
            file,
            on_bad_lines="warn",
            **import_settings
        )
        if isinstance(df, pd.DataFrame):
            return df
        else:
            return "Could not read file"
    else:
        return "File not found"

def analysis(df):
    return df

def test_func(*args):
    print("Called test function")
    print(*args)

if __name__ == '__main__':
    BulkFileAnalyser.main()  # Use bulk file analyser file to get a list of files and iterate through them for analysis

