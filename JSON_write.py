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
                        "Label 1": {
                              "read_line": "",
                              "regex": "",
                              "dtype": ""
                        },
                        "Label 2": {
                              "read_line": "",
                              "regex": "",
                              "dtype": ""
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
