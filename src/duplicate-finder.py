import argparse
import glob
import hashlib
import os
import shutil

VERSION = 'v1.0.1'
REPORT_CSV_HEADER = "ORIGINAL, DUPLICATE, COPIED/MOVED_DUPLICATE, ORIGINAL_COPY"


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


def check_report_file(arg_file):
    if os.path.isdir(arg_file):
        raise argparse.ArgumentTypeError(f"{arg_file} is not a file")
    dir_to_check = os.path.split(arg_file)[0]
    dir_to_check = dir_to_check if dir_to_check is None else "."
    if os.path.exists(dir_to_check) and os.access(dir_to_check, os.W_OK):
        return arg_file
    else:
        raise argparse.ArgumentTypeError(f"{arg_file} is not a writable file")


def check_dir_in_out(arg_dir_path):
    if os.path.exists(arg_dir_path) and os.path.isdir(arg_dir_path) and os.access(arg_dir_path, os.R_OK):
        return arg_dir_path
    else:
        raise argparse.ArgumentTypeError(f"{arg_dir_path} is not an existing readable directory")


def parse_arguments():
    parser = argparse.ArgumentParser(prog="duplicate-finder " + VERSION,
                                     description="Find and delete duplicate files. The oldest file according to its "
                                                 "CTIME is considerate the original one to keep. Here CTIME refers "
                                                 "to the last metadata change for specified path in UNIX while in "
                                                 "Windows, it refers to path creation time")
    parser.add_argument("-i", "--input", dest="input", nargs=1, required=True, type=check_dir_in_out,
                        help="Directory to scan files. It include all sub-folders at any depths. Hidden files are "
                             "excluded.")
    parser.add_argument("-o", "--output", dest="output", nargs=1, required=True, type=check_dir_in_out,
                        help="Directory where to move/copy files (with their sub-directory) that must be deleted "
                             "because duplicated. Files in output directory they will have 'DELETED_' in the name "
                             "prefix. The same directory will be also used for copy of the original file if required "
                             "(see option --copy original), they will have 'ORIGINAL_' in the name prefix.")
    parser.add_argument("-a", "--action", dest="action", nargs=1, required=False, choices=['c', 'm'], default='c',
                        help="Action to do when a duplicate is found: 'c' [Default] for copying file in output "
                             "directory, 'm' for move.")
    parser.add_argument('-c', '--copy_original', dest="copy_original", required=False, action='store_true',
                        help="Copy also original files in the output directory for comparison.")
    parser.add_argument("-r", "--report", dest="report", nargs=1, required=False, type=check_report_file,
                        help="Path of CSV(" + REPORT_CSV_HEADER + ") report file. Omit it for no report.")
    return parser.parse_args()


def main():
    input_cfg = parse_arguments()

    not_duplicate = {}

    file_list = glob.glob(os.path.join(input_cfg.input[0], "**/*"), recursive=True)
    file_list.sort(key=os.path.getctime)

    report_lines = []
    duplicates_found = 0
    for full_name in file_list:
        report_line = ""
        if os.path.isfile(full_name):
            sha_file = compute_hash(full_name)
            if sha_file in not_duplicate:
                print("Duplicates found:\n\tORIGINAL:", not_duplicate[sha_file]["path"], "\n\tDUPLICATED:", full_name)
                duplicates_found += 1
                if input_cfg.report is not None:
                    report_line += not_duplicate[sha_file]["path"] + "," + full_name + ","

                base_in_dir = str(input_cfg.input[0])
                sub_path, file_name = remove_base_dir(full_name, base_in_dir)
                out_file_clone = os.path.join(input_cfg.output[0], sub_path, "DELETE_" + file_name)
                copy_or_move_file(full_name, out_file_clone, input_cfg.action[0] == 'c')

                if input_cfg.report is not None:
                    report_line += out_file_clone + ","

                if input_cfg.copy_original:
                    sub_path, file_name = remove_base_dir(not_duplicate[sha_file]["path"], base_in_dir)
                    out_file_original = os.path.join(input_cfg.output[0], sub_path,
                                                     "ORIGINAL_" + file_name)
                    copy_or_move_file(not_duplicate[sha_file]["path"], out_file_original)

                    if input_cfg.report is not None:
                        report_line += out_file_clone

                if input_cfg.report is not None:
                    report_lines.append(report_line)

            else:
                not_duplicate.update({
                    sha_file: {
                        "path": full_name
                    }
                })

    if input_cfg.report is not None:
        report_lines = sorted(report_lines)
        with open(input_cfg.report[0], 'w') as fp:
            fp.write(REPORT_CSV_HEADER + '\n')
            for line in report_lines:
                fp.write(line + '\n')

    print("Found", duplicates_found, "duplicates\n")


if __name__ == "__main__":
    main()
