import hashlib
import shutil
import os
import argparse
import glob
import pathlib

REPORT_CSV_HEADER = "ORIGINAL, DUPLICATE, COPYED/MOVED_DUPLICATE, ORIGINAL_COPY"

def copy_or_move_file(from_, to, is_copy=True):
    head_tail = os.path.split(to)
    directory = head_tail[0]

    if not os.path.exists(directory):
        os.makedirs(directory)
    if is_copy:
        shutil.copyfile(from_, to)
    else:
        shutil.move(from_, to)


# return directory without root path and file name
def remove_base_dir(full_file_name, base_dir):
    if not base_dir.endswith('/'):
        base_dir += "/"

    file_name = os.path.basename(full_file_name)
    len_base_dir = len(base_dir)
    sub_path = full_file_name[len_base_dir:len_base_dir + (len(full_file_name) - len_base_dir - len(file_name))]
    return sub_path, file_name


def compute_hash(file_name):
    with open(file_name, "rb") as f:
        data = f.read()
        return hashlib.sha256(data).hexdigest()


def parse_arguments():
    parser = argparse.ArgumentParser(prog="DuplicateFider",
                                     description="Find and delete duplicate files. The oldest file is considerate the "
                                                 "original.")
    parser.add_argument("-i", "--input", dest="input", nargs=1, required=True, type=pathlib.Path,
                        help="Directory to scan files. It include all subfolders at any depts. Hidden files are "
                             "excluded.")
    parser.add_argument("-o", "--output", dest="output", nargs=1, required=True, type=pathlib.Path,
                        help="Directory where to move/copy files that must be deleted because duplicated, they will have 'ORIGINAL_' in the name prefix. The same"
                              "directory will be also used for copy of the original file if required (see option --copy original), they will have 'ORIGINAL_' in the name prefix.")
    parser.add_argument("-a", "--action", dest="action", nargs="?", required=False, choices=['c', 'm'], default='c',
                        help="Action to do when a duplicate is found: 'c' [Default] for copying file in output "
                             "directory, 'm' for move.")
    parser.add_argument('-c', '--copy_original', dest="copy_original", required=False, action='store_true',
                        help="Copy also original files in the output directory for comparison.")
    parser.add_argument("-r", "--report", dest="report", nargs=1, required=False, type=pathlib.Path,
                        help="Path of CSV(" + REPORT_CSV_HEADER + ") report file. Omit it for no report.")
    return parser.parse_args()


def main():
    print("Find Duplicates")
    input_cfg = parse_arguments()

    not_duplicate = {}

    file_list = glob.glob(os.path.join(input_cfg.input[0], "**/*"), recursive=True)
    file_list = sorted(file_list, key=lambda t: os.path.getctime(t))

    report_file = None
    report_line = ""
    if input_cfg.report is not None:
        report_file = open(input_cfg.report, "a")
        report_file.write(REPORT_CSV_HEADER + '\n')

    try:

        for full_name in file_list:
            
            if os.path.isfile(full_name):
                sha_file = compute_hash(full_name)
                if sha_file in not_duplicate:
                    print("Duplicates found, ORIGINAL:", not_duplicate[sha_file]["path"], ", DUPLICATED:", full_name)
                    if (report_file is not None): 
                        report_line += not_duplicate[sha_file]["path"] + "," + full_name + ","

                    base_in_dir = str(input_cfg.input[0])
                    sub_path, file_name = remove_base_dir(full_name, base_in_dir)
                    out_file_clone = os.path.join(input_cfg.output[0], sub_path, "DELETE_" + file_name)
                    copy_or_move_file(full_name, out_file_clone, input_cfg.action=='c')
                    
                    if (report_file is not None): 
                        report_line += out_file_clone + ","

                    if input_cfg.copy_original:
                        sub_path, file_name = remove_base_dir(not_duplicate[sha_file]["path"], base_in_dir)
                        out_file_original = os.path.join(input_cfg.output[0], sub_path,
                                                        "ORIGINAL_" + file_name)
                        copy_or_move_file(not_duplicate[sha_file]["path"], out_file_original)

                        if (report_file is not None): 
                            report_line += out_file_clone

                    if report_file is not None:
                        report_line += '\n'
                        
                else:
                    not_duplicate.update({
                        sha_file: {
                            "path": full_name
                        }
                    })
    finally:
        if report_file is not None:
            report_file.close()

    print("End, processing\n")


if __name__ == "__main__":
    main()
