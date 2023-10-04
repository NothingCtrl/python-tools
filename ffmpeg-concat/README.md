# `ffmpeg-concat/concat_ffmpeg.py`

A tool help scan all videos file an a path (include sub-folder) and call ffmpeg to concat these video files to one file

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