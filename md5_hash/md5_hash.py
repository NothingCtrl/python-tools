import os
import sys
import hashlib

if __name__ == "__main__":
    if len(sys.argv) < 2: 
        print("Please call with file path...")
    else:
        if not os.path.isfile(sys.argv[1]):
            print(f"Path {sys.argv[1]} is not valid a file!")
        else:
            with open(sys.argv[1], "rb") as f:
                file_hash = hashlib.md5()
                chunk = f.read(8192)
                while chunk:
                    file_hash.update(chunk)
                    chunk = f.read(8192)
            print(f"File {os.path.basename(sys.argv[1])} md5 hash: {file_hash.hexdigest()}")