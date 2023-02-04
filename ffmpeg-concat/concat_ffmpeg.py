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
from natsort import natsorted, ns
import hashlib
# from operator import itemgetter

VIDEO_EXTENSION = ("mp4", "mpeg", "mpg", "mkv")

def md5_hash(text: str) -> str:
    return hashlib.md5(text.encode('utf8')).hexdigest()

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

def ffmpeg_concat(source_file: str, output_file: str) -> bool:
    cmd = ["ffmpeg", "-safe", "0", "-f", "concat", "-i", source_file, "-c", "copy", output_file]
    # if encode_mode:
    #     cmd = ["ffmpeg", "-safe", "0", "-f", "concat", "-i", source_file, "-qscale", "0", "-vcodec", "mpeg4", output_file]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if os.path.isfile(output_file):
        return True
    print("[ERROR!!!] ffmpeg_concat error:\n===\n")
    print(result.stdout)
    return False

def ffmpeg_chapter(video_file: str, chapter_source_file: str, video_total_time: float, output_file: str) -> bool:

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
                end = int(video_total_time * 1000)
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
        if os.path.isfile(output_file):
            print(f"- Delete file {output_file}")
            os.unlink(output_file)
        result2 = subprocess.run(["ffmpeg", "-i", video_file, "-i", output_metadata_file, "-map_metadata", "1", "-codec", "copy", output_file],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if os.path.isfile(output_file):
            os.unlink(output_metadata_file)
            return True
        else:
            print("[ERROR!!!] Add video chapter(s) failed\n===\n")
            print(result2.stdout)
    else:
        print("[ERROR!!!] Generate default metadata file error!\n===\n")
        print(result.stdout)
    return False

def ffmpeg_fix_audio_sync(input_video: str, temp_dir_path: str):
    ext = input_video.split(".").pop()
    video_size = os.path.getsize(input_video)
    video_name_out = os.path.basename(input_video).replace(f".{ext}", "") + f"_{md5_hash(input_video + str(video_size))[-8:]}_a_fixed.{ext}"
    output_video = os.path.join(temp_dir_path, video_name_out)
    if os.path.isfile(output_video):
        return output_video.replace("\\", "/")
    cmd = ["ffmpeg", "-async", "25", "-i", input_video, "-c:v", "copy", "-c:a", "copy", "-r", "25", output_video]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if os.path.isfile(output_video):
        return output_video.replace("\\", "/")
    print(f"Run fix video for file {input_video} error!")
    print(result.stdout)
    return ""

def ffmpeg_re_encode(input_video: str, temp_dir_path: str):
    ext = input_video.split(".").pop()
    video_size = os.path.getsize(input_video)
    video_name_out = os.path.basename(input_video).replace(f".{ext}", "") + f"_{md5_hash(input_video + str(video_size))[-8:]}_v_fixed.{ext}"
    output_video = os.path.join(temp_dir_path, video_name_out)
    if os.path.isfile(output_video):
        return output_video.replace("\\", "/")
    # cmd = ["ffmpeg", "-i", input_video, "-c", "copy", "-bsf:v", "h264_mp4toannexb", "-f", "mpegts", "-r", "30", output_video]
    # cmd = ["ffmpeg", "-i", input_video, "-c:v", "libx264", "-c:a", "aac", "-ar", "44100", "-r", "30", output_video]
    cmd = ["ffmpeg", "-i", input_video, "-c:v", "copy", "-c:a", "aac", "-ar", "44100", "-r", "30", output_video]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if os.path.isfile(output_video):
        return output_video.replace("\\", "/")
    print(f"Run encode for file {input_video} error!")
    print(result.stdout)
    return ""

if __name__ == "__main__":
    print("*-" * 40)
    print("=== CONCAT MULTI-VIDEO FILE TO SINGLE FILE WITH CHAPTERS INFO ===")
    print("*-" * 40)
    start_time = time.time()
    source_dir = input("Video source folder: ")
    output_dir = input("Output folder (blank to using same source folder): ")
    print("Running config, input '1' or 'y' to confirm, ENTER to ignore...")
    dry_run = input("  - Dry run mode? (default: NO) ")
    re_encode_first = input("  - Re-encode video(s) audio? (default: NO) ")
    if re_encode_first not in ('1', 'y'):
        re_encode_first = False
        fix_audio_sync = input("  - Run audio sync fix? (default: NO) ")
    else:
        re_encode_first = True
        fix_audio_sync = ""
    # encode_video = input("Encode video (blank to using copy mode): ")
    current_dir = os.path.dirname(os.path.realpath(__file__))
    # ---
    dry_run = True if dry_run in ('1', 'y') else False
    temp_dir = os.path.join(current_dir, "temp")
    if not os.path.isdir(temp_dir):
        os.mkdir(temp_dir)

    chapter_data = []
    total_time = 0

    base_name = os.path.basename(source_dir).replace(" ", "_") if os.path.basename(source_dir).replace(" ", "_") else f'OUTPUT_{int(start_time)}'
    debug_file = os.path.join(temp_dir, "DEBUG_" + base_name).replace("\\", "/") + ".json"
    merged_video = os.path.basename(source_dir) if os.path.basename(source_dir) else f"OUTPUT_{int(start_time)}"
    if output_dir:
        merged_video = os.path.join(output_dir, merged_video).replace("\\", "/") + "_merged.mp4"
    else:
        merged_video = os.path.join(source_dir, merged_video).replace("\\", "/") + "_merged.mp4"

    chapters_video = merged_video.replace("_merged.mp4", "_Chapters.mp4")

    if os.path.isdir(source_dir):
        all_items = scan_folder(source_dir)
        # sort item like Windows sort
        all_items = natsorted(all_items, alg=ns.IGNORECASE)
        for ai in all_items:
            if os.path.isfile(ai) and ai.split(".")[-1].lower() in VIDEO_EXTENSION \
                    and os.path.basename(merged_video) not in ai and os.path.basename(chapters_video) not in ai:
                dir_name = os.path.basename(os.path.dirname(ai))
                video_time = get_length(ai)
                chapter_data.append({'start': int(total_time) + 1, 'name': f"{dir_name} / {os.path.basename(ai)}", 'path': ai, 'length': video_time})
                total_time += video_time
    else:
        print("- Error, source video folder is not exists!")
        exit()

    # sort item like Windows sort
    # chapter_data = natsorted(chapter_data, key=itemgetter(*['path']), alg=ns.IGNORECASE)

    if re_encode_first and not dry_run:
        print("- RUN re-encode video...")
        idx = 0
        for item in chapter_data:
            fix_file = ffmpeg_re_encode(item['path'], temp_dir)
            if fix_file:
                chapter_data[idx]['path'] = fix_file
            idx += 1

    if fix_audio_sync in ("1", "y") and not dry_run:
        print("- RUN audio sync fix...")
        idx = 0
        for item in chapter_data:
            fix_file = ffmpeg_fix_audio_sync(item['path'], temp_dir)
            if fix_file:
                chapter_data[idx]['path'] = fix_file
            idx += 1

    # debug data
    with open(debug_file, "w+") as f:
        json.dump({'chapter_data': chapter_data, 'total_time': total_time}, f, indent=4)

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
    if dry_run:
        print("- Dry run mode, program exit...")
        exit()
    print("- RUN file(s) concat...")

    if os.path.isfile(merged_video):
        print(f"- Delete file: {merged_video}")
        os.unlink(merged_video)
    ok_concat = ffmpeg_concat(concat_list, merged_video)
    if ok_concat:
        print("- RUN update chapter(s) metadata...")
        # create chapter info
        ok_chapter = ffmpeg_chapter(merged_video, chapter_file, total_time, chapters_video)
        print("\n=======================================")
        if ok_chapter:
            print(f"Final result: {chapters_video}")
            os.unlink(merged_video)
        else:
            print(f"Add chapter failed... output video without chapter: {merged_video}")
    else:
        print("Run concat error!")
