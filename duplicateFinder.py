import hashlib
import shutil
import os
import argparse
import sys
import glob

def computeHash(file_name):
    with open(file_name, "rb") as f:
        data = f.read()
        return hashlib.sha256(data).hexdigest()

def parseArguments():
    parser = argparse.ArgumentParser(prog="DuplicateFider", description="Find and delete duplicate files.")
    parser.add_argument("-i", "--input", dest="input", nargs="1", required=True, help="Directory to scan files. It include all subfolder at any depts. Hidden files are excluded.")
    parser.add_argument("-o", "--output", dest="output", nargs="1", required=True, help="Directory where to move/copy file that must be delete because duplicated.")
    parser.add_argument("-a", "--action", dest="action", nargs="?", required=False, choices=['c', 'm'], default='c', help="Action to do when a duplicate is found: 'c' [Default] for copying file in output directory, 'm' for move.")
    return parser.parse_args()

def main():
    print("Find Duplicates")
    input_cfg = parseArguments()

    not_duplicate = {}
    duplicates = {}

    file_list = glob.glob(os.path.join(FILES_DIR_DELETED, "**/*"), recursive=True)
    
    # Iterate directory
    for full_name in file_list:
        # check if current file is a file
        if os.path.isfile(full_name):
            sha_file = computeHash(full_name)
            if sha_file in not_duplicate:
                duplicates.update({
                    sha_file: {
                        "path": full_name,
                        "original": not_duplicate[sha_file]["path"]
                    }
                })

                # check this code block
                base_out_dir = input_cfg.output
                if (not base_out_dir.endswith('/')):
                    base_dir += "/"

                out_file_clone = os.path.join(FILES_DIR_DELETED, "DELETE_" + file_path)
                shutil.copyfile(full_name, out_file_clone)
 
                out_file_original = os.path.join(FILES_DIR_DELETED, "ORIGINAL_" + os.path.basename(not_duplicate[sha_file]["path"]))
                shutil.copyfile(not_duplicate[sha_file]["path"], out_file_original)
            else:
                not_duplicate.update({
                    sha_file: {
                        "path": full_name
                    }
                })
        else:
            print("Error", file_path, "is a folder!")

    print("End, report\n", duplicates)


if __name__ == "__main__":
    main()
