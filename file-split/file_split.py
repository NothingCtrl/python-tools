# -*- coding: utf-8 -*-
import os
import sys
import unicodedata
import argparse

if getattr(sys, 'frozen', False):
    # frozen
    from sys import exit

parser = argparse.ArgumentParser()

parser.add_argument("--input", "-i", help="input file for split or join")
parser.add_argument("--output", "-o", help="output folder (split mode) or output file (join mode)")
parser.add_argument("--mode", "-m", help="mode: join or split, default is: split", default='split')
parser.add_argument("--size", "-s", help="set split file size in bytes, default is: 104857600",
                    default=f'{1024 * 1024 * 100}')

args = parser.parse_args()


def split_file(source_file: str, output_dir: str, split_size: int):
    """
    Split big file to small chunk
    :param split_size:
    :param source_file:
    :param output_dir:
    :return:
    """

    def _file_name_encode_fix(file_name):
        error = True
        while error:
            try:
                str.encode(file_name)
                error = False
            except UnicodeEncodeError:
                file_name = unicodedata.normalize('NFKD', file_name).encode('utf-8', 'ignore')
            except:
                error = False
        return file_name

    # Make a destination folder if it doesn't exist yet
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    part_num = 0
    buffering = 1024 * 1024 * 10
    if buffering > split_size:
        buffering = split_size
    if buffering > os.path.getsize(source_file):
        buffering = -1
    input_file = open(source_file, 'rb', buffering=buffering)  # 10mb
    while True:
        part_num += 1
        chunk = input_file.read(buffering)
        # End the loop if we have hit EOF
        if not chunk:
            break
        filename = os.path.join(output_dir,
                                "{0}_file_part_{1:0=3d}".format(_file_name_encode_fix(os.path.basename(source_file)),
                                                                part_num))
        print(f"  - File part: {filename}")
        dest_file = open(filename, 'wb')
        dest_file.write(chunk)
        total_read = buffering
        while total_read < split_size:
            chunk = input_file.read(buffering)
            if not chunk:
                break
            dest_file.write(chunk)
            total_read += buffering
        # Explicitly close
        dest_file.close()
    # Explicitly close
    input_file.close()

    print("\r\n----")
    print(f"- Split file done, total parts: {part_num}")


def join_file(input_file: str, output_file: str, read_size: int = 10485760):
    """
    Join all file in source_dir
    :param input_file:
    :param output_file: the output of join file
    :param read_size: if -1, read whole file to memory, default 1024*1024*10 = 10mb
    :return:
    """
    if os.path.isfile(output_file):
        print("\r\nERROR")
        print("- Output file is exist!")
        exit()
    # make output dir if needed
    if not os.path.exists(os.path.dirname(output_file)):
        os.mkdir(os.path.dirname(output_file))
    # Create a new destination file
    output_file_w = open(output_file, 'wb')
    # Get a list of the file parts
    input_dir = os.path.dirname(input_file)
    base_name = os.path.basename(input_file).split('_file_part_')[0] if '_file_part_' in input_file else ''
    if not base_name:
        print("\r\nERROR:")
        print("- The input file name is not correct format!")
        exit()

    parts = os.listdir(input_dir)
    # Sort them by name (remember that the order num is part of the file name)
    parts.sort()
    # Go through each portion one by one
    for file in parts:
        if base_name in file:
            print(f"  - Joining file: {file}")
            # Assemble the full path to the file
            path = os.path.join(input_dir, file)
            # Open the part
            input_file = open(path, 'rb')
            while True:
                # Read all bytes of the part
                file_bytes = input_file.read(read_size)
                # Break out of loop if we are at end of file
                if not file_bytes:
                    break
                # Write the bytes to the output file
                output_file_w.write(file_bytes)
            # Close the input file
            input_file.close()

    # Close the output file
    output_file_w.close()
    print("\r\n----")
    print(f"- Joined, output file: {output_file}")


if __name__ == '__main__':
    join_mode = args.mode == 'join'
    split_file_size = int(args.size)

    if not args.input or not args.output:
        print("usage \"-h\" for help")
        print("----")
        print("INPUT (-i) and OUTPUT (-o) params are required!. Default mode is SPLIT file, use \"-m join\" for join files.")
        exit()

    print(f'---- MODE: {"JOIN FILES" if join_mode else "SPLIT FILE"} ----')
    print(f"- INPUT: {args.input}")
    print(f"- OUTPUT: {args.output}")

    if join_mode:
        join_file(args.input, args.output)
    else:
        print(f"- SPLIT size (MB): {split_file_size}")
        split_file(args.input, args.output, split_file_size)
