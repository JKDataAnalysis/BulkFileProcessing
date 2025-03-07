import os
import sys
import importlib

import_settings = {
   "Tekscan Footscan SAM (text)": {
     "file_type": {
       "type": "csv",
       "label": "Tekscan SAM",
     },
      "clean_file_func": {
         "module": "/home/jon/.config/JetBrains/PyCharmCE2024.3/scratches/Scratch_TestCall.py",
         "func": "test_func_test_call"
      },
     "read_file_func": {
         "module": "",
         "func": "read_text_file"
      },
     "analysis_func": {
         "module": "AnalysisTemplate",
         "func": "test_func"
      },
      "import_param": {
         "sep": ",",
         "header": 8,
         "engine": "python",
         "skipfooter": 4,
        "dtype": {"Time":  "float", "Frame":  "int"}
      }
   },
   "Kistler Bioware (text)": {
      "file_type": {
         "type": "txt",
         "label": "Kistler Bioware"
      },
      "clean_file_func": {
         "module": "",
         "func": ""
      },
      "read_file_func": {
         "module": "",
         "func": "read_text_file"
      },
     "analysis_func": {
         "module": "",
         "func": ""
      },
      "import_param": {
         "sep": "\t",
         "header": 19
      }
   }
}


# Should be outwith class
def check_dict_keys(d, key_list):
    for key in key_list:
        if key not in d:
            return key  # Return key not found
    return False  # No missing keys found


# Should be within BuildCue class
def check_import_setting_keys(dict_to_check, check_list):
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


def check_import_setting_func(func_dict):
    functions = {}
    for d in func_dict:
        # Check function unless it's the clean_file_func (optional) AND there is no value set for func
        if not (d == "clean_file_func" and not func_dict[d]['func']):  # Empty string will return as True
            r = check_functions(func_dict[d])
            if isinstance(r, str):  # If returned an error message
                return d + ': ' + r
            else:
                functions[d] = r
    return functions


def check_functions(func_to_check):
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


def main():
    # subset dictionary to selected source
    selected_import_settings = import_settings['Tekscan Footscan SAM (text)']

    # Dictionary of keys that selected import settings must contain to be valid
    required_keys_list = {
        "file_type": ["type", "label"],
        "clean_file_func": ["module", "func"],
        "read_file_func": ["module", "func"],
        "analysis_func": ["module", "func"],
        "import_param": []
    }

    # Check selected dictionary against required keys
    key_error = check_import_setting_keys(selected_import_settings, required_keys_list)
    if key_error:
        print("Key error:", key_error)
    else:
        print('Keys OK')

    # Filter dictionary keys for only those that end in '_func'
    func_dict = {k: v for k, v in selected_import_settings.items() if k.endswith('_func')}
    file_handling_funcs = check_import_setting_func(func_dict)
    if not isinstance(file_handling_funcs, dict):
        print("Function error:", file_handling_funcs)
    else:
        print('Functions OK')

        # Functions can now be called by filtering the dictionary for the required key/ value pair as:
        file_handling_funcs['read_file_func']()
        file_handling_funcs['analysis_func']()


if __name__ == '__main__':
    main()