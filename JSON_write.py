"""
Quick utility to pretty print dictionary with analysis type profiles information to JSON
"""
import os
import sys
import json

import_settings = {
      "Balance analysis: Tekscan Footscan SAM (text file)": {
            "file_type": {
                  "type": "csv",
                  "label": "Tekscan SAM"
            },
            "clean_file_func": {
                  "module": "",
                  "func": "",
                  "parameters": {}
            },
            "read_file_func": {
                  "module": "",
                  "func": "read_text_file",
                  "parameters": {
                        "sep": ",",
                        "header": 7,
                        "engine": "python",
                        "skipfooter": 4,
                        "dtype": {
                              "Time": "float",
                              "Frame": "int"
                        }
                  }
            },
            "analysis_func": {
                  "module": "",
                  "func": "temp_analysis_func",
                  "parameters": {}
            },
            "read_header_func": {
                  "module": "",
                  "func": "read_header",
                  "parameters": {},
                  "headers": {
                        "Sample rate": {
                              "read_line": 6,
                              "regex": r"\d+$",
                              "data_type": "int"
                        },
                        "Date": {
                              "read_line": 8,
                              "regex": r"\d{1,2}\b.{1,}\b\d{2}[:]\d{2}[:]\d{2}$",
                              "data_type": "date_time",
                              "date_time_format": "%d %B %Y %H:%M:%S"
                        },
                        "Filename": {
                              "read_line": 5,
                              "regex": r"\w{1,}.fsx$",
                              "data_type": "str"
                        }
                  }
            }
      },
      "Balance analysis: Kistler Bioware (text fle)": {
            "file_type": {
                  "type": "txt",
                  "label": "Kistler Bioware"
            },
            "clean_file_func": {
                  "module": "",
                  "func": "",
                  "parameters": {}
            },
            "read_file_func": {
                  "module": "",
                  "func": "read_text_file",
                  "parameters": {
                        "sep": "\t",
                        "header": 19
                  }
            },
            "analysis_func": {
                  "module": "",
                  "func": "temp_analysis_func",
                  "parameters": {}
            },
            "read_header_func": {
                  "module": "",
                  "func": "read_header",
                  "parameters": {},
                  "headers": {}
            }
      }
}

data_def_file = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "DataFileImportSettings.json")
with open(data_def_file, "w") as fp:
    json.dump(import_settings, fp, indent=6)

print("File written to:", data_def_file)
