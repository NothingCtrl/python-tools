# python 3
# Use for:
# - Scan video file(s) in a directory (include sub-dir)
# - Generate a list of file to concat
# - Generate a chapter list (start time - name)
# - Call ffmpeg to concat all video files from list above to one file
# - Call ffmpeg to add chapters from chapter list above created file
# ---

import os
import subprocess
import re
import json
import time

VIDEO_EXTENSION = ("mp4", "mpeg", "mpg", "mkv")

def scan_folder(path: str) -> list:
    items = [path.replace("\\", "/")]
    if not os.path.isfile(path):
        path_items = os.listdir(path)
        for pi in path_items:
            item_path = os.path.join(path, pi)
            if os.path.isfile(item_path):
                items.append(item_path.replace("\\", "/"))
            else:
                items += scan_folder(item_path)
    return items

def get_length(filename):
    """
    Return video length in second
    :param filename:
    :return:
    """
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

def generate_concat_list(chapter_info: list) -> str:
    text = ""
    for item in chapter_info:
        if text:
            text += "\n"
        i_path = item['path'].replace(" ", "\ ").replace("'", "\\'")
        text += f"file {i_path}"
    return text

def generate_chapter_info(chapter_info: list) -> str:
    def second_to_time(num: float) -> str:
        if num < 60:
            return f"00:00:{num:02}"
        if 60 <= num < 3600:
            minute = int(num/60)
            second = num - minute*60
            return f"00:{minute:02}:{second:02}"
        hour = int(num / 3600)
        minute = int((num - (hour*3600))/60)
        second = num - (hour*3600) - (minute * 60)
        return f"{hour:02}:{minute:02}:{second:02}"
    text = ""
    for item in chapter_info:
        if text:
            text += "\n"
        text += f"{second_to_time(item['start'])} {item['name']}"
    return text

def ffmpeg_concat(source_file: str, output_file: str):
    cmd = ["ffmpeg", "-safe", "0", "-f", "concat", "-i", source_file, "-c", "copy", output_file]
    # if encode_mode:
    #     cmd = ["ffmpeg", "-safe", "0", "-f", "concat", "-i", source_file, "-qscale", "0", "-vcodec", "mpeg4", output_file]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return result.stdout

def ffmpeg_chapter(video_file: str, chapter_source_file: str, video_total_time: float) -> str:

    def metadata_with_chapter():
        chapters = list()
        with open(chapter_source_file, 'r', encoding='utf8', errors='ignore') as f:
            for line in f:
                x = re.match(r"(\d{2}):(\d{2}):(\d{2}) (.*)", line)
                hrs = int(x.group(1))
                mins = int(x.group(2))
                secs = int(x.group(3))
                title = x.group(4)

                minutes = (hrs * 60) + mins
                seconds = secs + (minutes * 60)
                timestamp = (seconds * 1000)
                chap = {
                    "title": title,
                    "startTime": timestamp
                }
                chapters.append(chap)

        text = ""

        for i in range(len(chapters)):
            chap = chapters[i]
            title = chap['title']
            start = chap['startTime']
            if i == len(chapters) - 1:
                end = (int(video_total_time) + 1) * 1000
            else:
                end = chapters[i + 1]['startTime'] - 1
            text += f"""
[CHAPTER]
TIMEBASE=1/1000
START={start}
END={end}
title={title}
"""

        with open(output_metadata_file, "ab") as meta_file:
            meta_file.write(text.encode('utf8'))

    output_metadata_file = os.path.join(os.path.dirname(video_file), "FFMETADATAFILE.txt")
    if os.path.isfile(output_metadata_file):
        os.unlink(output_metadata_file)
    result = subprocess.run(["ffmpeg", "-i", video_file, "-f", "ffmetadata", output_metadata_file],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if os.path.isfile(output_metadata_file):
        # add chapter info to metadata file
        metadata_with_chapter()
        # add metadata file back to video file
        output_video = video_file.replace('_merged.mp4', '_Chapters.mp4')
        if os.path.isfile(output_video):
            print(f"- Delete file {output_video}")
            os.unlink(output_video)
        result2 = subprocess.run(["ffmpeg", "-i", video_file, "-i", output_metadata_file, "-map_metadata", "1", "-codec", "copy", output_video],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if os.path.isfile(output_video):
            return output_video
        else:
            print("Generate chapter failed")
            print(result2.stdout)
    else:
        print("Generate default metadata file error!")
        print(result.stdout)
    return ""

def ffmpeg_fix_audio_sync(input_video: str, temp_dir_path: str):
    ext = input_video.split(".").pop()
    video_name_out = os.path.basename(input_video).replace(f".{ext}", "") + f"_fixed.{ext}"
    output_video = os.path.join(temp_dir_path, video_name_out)
    if os.path.isfile(output_video):
        os.unlink(output_video)
    cmd = ["ffmpeg", "-async", "25", "-i", input_video, "-vcodec", "copy", "-acodec", "copy", "-r", "25", output_video]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if os.path.isfile(output_video):
        return output_video.replace("\\", "/")
    print(f"Run fix video for file {input_video} error!")
    print(result.stdout)
    return ""

if __name__ == "__main__":
    print("*-" * 40)
    print("=== CONCAT MULTI-VIDEO FILE TO SINGLE FILE WITH CHAPTERS INFO ===")
    print("*-" * 40)
    start_time = time.time()
    source_dir = input("Scan video from folder: ")
    output_dir = input("Output folder (blank to using same source folder): ")
    fix_video_first = input("Run fix for audio sync (in-case result audio out-of-sync, enter to ignore): ")
    # encode_video = input("Encode video (blank to using copy mode): ")
    current_dir = os.path.dirname(os.path.realpath(__file__))
    # ---
    temp_dir = os.path.join(current_dir, "temp")
    if not os.path.isdir(temp_dir):
        os.mkdir(temp_dir)

    chapter_data = []
    total_time = 0
    if os.path.isdir(source_dir):
        all_items = scan_folder(source_dir)
        for ai in all_items:
            if os.path.isfile(ai) and ai.split(".")[-1].lower() in VIDEO_EXTENSION:
                dir_name = os.path.basename(os.path.dirname(ai))
                video_time = get_length(ai)
                chapter_data.append({'start': int(total_time) + 1, 'name': f"{dir_name} / {os.path.basename(ai)}", 'path': ai, 'length': video_time})
                total_time += video_time

    if fix_video_first in ("1", "y", "Y"):
        print("- RUN audio sync fix...")
        idx = 0
        for item in chapter_data:
            fix_file = ffmpeg_fix_audio_sync(item['path'], temp_dir)
            if fix_file:
                chapter_data[idx]['path'] = fix_file
            idx += 1

    base_name = os.path.basename(source_dir).replace(" ", "_") if os.path.basename(source_dir).replace(" ", "_") else f'OUTPUT_{int(start_time)}'
    debug_file = os.path.join(temp_dir, "DEBUG_" + base_name).replace("\\", "/") + ".json"
    with open(debug_file, "w+") as f:
        json.dump(chapter_data, f, indent=4)

    # generate list of concat files
    print("- Generate concat file list...")
    concat_list = os.path.join(temp_dir, "CONCAT_" + base_name).replace("\\", "/") + ".txt"
    with open(concat_list, "wb+") as f:
        f.write(generate_concat_list(chapter_data).encode('utf8'))
        f.close()

    # generate chapter text
    print("- Generate chapters metadata...")
    chapter_file = os.path.join(temp_dir, "CHAPTER_" + base_name).replace("\\", "/") + ".txt"
    with open(chapter_file, "wb+") as f:
        f.write(generate_chapter_info(chapter_data).encode('utf8'))
        f.close()

    # run concat
    print("- RUN file concat...")
    video_basename = os.path.basename(source_dir) if os.path.basename(source_dir) else f"OUTPUT_{int(start_time)}"
    if output_dir:
        output_file = os.path.join(output_dir, video_basename).replace("\\", "/") + "_merged.mp4"
    else:
        output_file = os.path.join(source_dir, video_basename).replace("\\", "/") + "_merged.mp4"
    if os.path.isfile(output_file):
        print(f"- Delete file: {output_file}")
        os.unlink(output_file)
    output = ffmpeg_concat(concat_list, output_file)
    if os.path.isfile(output_file):
        # create chapter info
        video_file_out = ffmpeg_chapter(output_file, chapter_file, total_time)
        print("\n=======================================")
        if video_file_out:
            print(f"Final result: {video_file_out}")
            os.unlink(output_file)
        else:
            print(f"Add chapter failed... output video without chapter: {output_file}")
    else:
        print("Run concat error!")
        print(output)
