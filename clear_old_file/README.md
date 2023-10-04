# Clear Old File/Folder

Delete old folder / file based on file ages and disk free size

### Usages

* Delete all file and folder in path `/foo/bar` if folder or file older than `10 days`:
  ```
  python3 clear_old_file.py --path /foo/bar --ages 10
  ```
* Delete direct sub-directory of path `/foo/bar` only when disk free size below `20GB` and folder older than `3 days`: 
  ```
  python3 clear_old_file.py --path /foo/bar --ages 3 --mode folder --disk-free-trigger 20 --folder-level 1
  ```

To debug, add param: `--debug 1`, for more information call: `python3 clear_old_file.py --help`

### Release Files

* The release file in `release/linux_x64` is build by `pyinstaller` on Ubuntu 20.04 with Python 3.9  
* The release file in `release/windows_x64` is build by `pyinstaller` on Windows 11 with Python 3.9