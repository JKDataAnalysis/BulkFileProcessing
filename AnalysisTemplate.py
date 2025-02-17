import BulkFileAnalyser


def external_read_info():
    return({"engine": "python",
            "skipfooter": 4})

if __name__ == '__main__':
    # Whether to use the standard function in BulkFileAnalyzer to read files based upon their import settings in the
    # DataFileSPec.sv file or to use custom_read_file function in this file
    use_custom_file_read = True
    BulkFileAnalyser.main()  # Use bulk file analyser file to get a list of files and iterate through them for analysis