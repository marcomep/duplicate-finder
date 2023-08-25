import hashlib
import shutil
import os
import argparse
import glob


# return directory without root path and file name
def remove_base_dir(full_file_name, base_dir):
    if not base_dir.endswith('/'):
        base_dir += "/"

    file_name = os.path.basename(full_file_name)
    len_base_dir = len(base_dir)
    sub_path = full_file_name[len_base_dir:len_base_dir - len(file_name)]
    return sub_path, file_name


def compute_hash(file_name):
    with open(file_name, "rb") as f:
        data = f.read()
        return hashlib.sha256(data).hexdigest()


def parse_arguments():
    parser = argparse.ArgumentParser(prog="DuplicateFider",
                                     description="Find and delete duplicate files. The oldest file is considerate the "
                                                 "original.")
    parser.add_argument("-i", "--input", dest="input", nargs=1, required=True,
                        help="Directory to scan files. It include all subfolder at any depts. Hidden files are "
                             "excluded.")
    parser.add_argument("-o", "--output", dest="output", nargs=1, required=True,
                        help="Directory where to move/copy file that must be delete because duplicated.")
    parser.add_argument("-a", "--action", dest="action", nargs="?", required=False, choices=['c', 'm'], default='c',
                        help="Action to do when a duplicate is found: 'c' [Default] for copying file in output "
                             "directory, 'm' for move.")
    return parser.parse_args()


def main():
    print("Find Duplicates")
    input_cfg = parse_arguments()

    not_duplicate = {}
    duplicates = {}

    file_list = glob.glob(os.path.join(input_cfg.input[0], "**/*"), recursive=True)
    file_list = sorted(file_list, key=lambda t: os.path.getctime(t))

    # Iterate directory
    for full_name in file_list:
        # check if current file is a file
        if os.path.isfile(full_name):
            sha_file = compute_hash(full_name)
            if sha_file in not_duplicate:
                duplicates.update({
                    sha_file: {
                        "path": full_name,
                        "original": not_duplicate[sha_file]["path"]
                    }
                })

                base_in_dir = input_cfg.input
                sub_path, file_name = remove_base_dir(full_name, base_in_dir)
                out_file_clone = os.path.join(input_cfg.output, sub_path, "DELETE_" + file_name)
                shutil.copyfile(full_name, out_file_clone)

                sub_path, file_name = remove_base_dir(not_duplicate[sha_file]["path"], base_in_dir)
                out_file_original = os.path.join(input_cfg.output, sub_path,
                                                 "ORIGINAL_" + file_name)
                shutil.copyfile(not_duplicate[sha_file]["path"], out_file_original)
            else:
                not_duplicate.update({
                    sha_file: {
                        "path": full_name
                    }
                })
        else:
            print("Error", full_name, "is a folder!")

    print("End, report\n", duplicates)


if __name__ == "__main__":
    main()
