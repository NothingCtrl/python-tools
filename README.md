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
    
### `network_status_check.py`: check for network and reboot OS if failed / (or) refresh interface (Windows)

* help: `python3 network_status_check.py -h`
* usage: 
    * `python3 network_status_check.py --url http://192.168.1.1` (reboot OS if failed)
    * `python3 network_status_check.py --url http://192.168.1.1 -ri "Local Area Connection"` (refresh interface if failed)
    
### `ffmpeg-concat/concat_ffmpeg.py`: a tool help scan all videos file an a path (include sub-folder) and call ffmpeg to concat these video files to one file

The merged file also have chapter list segment by video items. 

* requirement:
    * This script required install some library in `requirements.txt`
    * `ffmpeg` command must call-able in command-line

* usage:
    * `python3 concat_ffmpeg.py`
    * Input the video source folder
    * Input the output folder
    * Add some option if needed, enter to skip (default is option 0), list of options are:
        * 0 - run ffmpeg concat with copy mode (very fast and video quality is keep same as source)
        * 1 - run audio sync fix for all input video before run concat, using this option in-case the result audio out-of-sync
        * 2 - run audio encode for all input video before run concat, using this option in-case the result video time is not correct
        * 3 - run audio and video encode for all input video, using this option in-case video input not in same format
        * 4 - scale all input video to same size, using this option in-case video input have difference resolution