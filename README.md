# Python Tools

> **python 3** is required

## General info

If a build file (executable file) exist, the OS using to build file is:
* for Windows: Windows 10 AMD64
* for Linux: Ubuntu 20.04 AMD64

## Tools

### `file_split.py`: Split and join file

* help: `python3 file_split.py -h`
* split file (default mode): `python3 file_split.py -i path_of_input_file -o path_of_output_dir`
    * Set split file size: default is `104857600 bytes` (100MB), use `--size \ -s` to change this value
* join split files: `python3 file_split.py -m join -i path_of_first_splited_file -o path_of_join_file`

### `login_to_pod.py`: help tool find and login to kubernetes pod

* help: `python3 login_to_pod.py -h`
* usage: `python3 login_to_pod.py -p pod-name`
    * The `pod-name` is not need exactly match