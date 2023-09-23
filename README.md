# duplicate-finder
**duplicate-finder** is simple command line tool to find duplicate files and remove them.

## Download application

### Method 1: download binaries for Linux

On Linux the easiest way to obtain duplicate-finder tool is to download the binaries (all modern distros and versions are supported.

- For Linux you can download the last version [here](https://duckduckgo.com)

### Method 2: download python script for all Operating System, including Windows & MacOS

It's always possible to download the Python source code and run it on a Python3 interpreter on all O.S.

Requirements
- Python 3 version >= 3.10. On older versions find-duplicate can works but it has not been tested.

You can download the source code clicking [here](https://duckduckgo.com) or cloning this repository (it require a Git client installed) with the following command:

```bash
git clone https://duckduckgo.com
```

## Run the application
If you have download binaries (method 1) to run duplicate-finder you have simply unzip the archive downloaded and run it from command line.

```
./duplicate-finder *options*
```

If you have download source code (method 2) or cloned repository you have simply:

1. unzip the archive if you have downloaded the source code 
2. run the Python script in *src* folder with Python3 runtime.

```bash
python3 duplicate-finder.py *options*
```

For understand the options you can use the help provided with duplicate-finder. It is also reported below.

```
usage: duplicate-finder v1.0 [-h] -i INPUT -o OUTPUT [-a [{c,m}]] [-c] [-r REPORT]

Find and delete duplicate files. The oldest file according to its CTIME is considerate the original one to keep. Here CTIME refers to the last metadata change for specified path in UNIX while in Windows, it refers to path creation time

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Directory to scan files. It include all sub-folders at any depths. Hidden files are excluded.
  -o OUTPUT, --output OUTPUT
                        Directory where to move/copy files that must be deleted because duplicated, they will have 'ORIGINAL_' in the name prefix. The samedirectory will be also used for copy of the original file if required (see option --copy original), they will have 'ORIGINAL_' in the name prefix.
  -a [{c,m}], --action [{c,m}]
                        Action to do when a duplicate is found: 'c' [Default] for copying file in output directory, 'm' for move.
  -c, --copy_original   Copy also original files in the output directory for comparison.
  -r REPORT, --report REPORT
                        Path of CSV(ORIGINAL, DUPLICATE, COPIED/MOVED_DUPLICATE, ORIGINAL_COPY) report file. Omit it for no report.
```

