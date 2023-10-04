# `file_split.py`

Split and join file

* help: `python3 file_split.py -h`
* split file (default mode): `python3 file_split.py -i path_of_input_file -o path_of_output_dir`
    * Set split file size: default is `104857600 bytes` (100MB), use `--size \ -s` to change this value
* join split files: `python3 file_split.py -m join -i path_of_first_splited_file -o path_of_join_file`