## Script Execute

Using to execute all script files in the `scripts` folder and get output, the script must be fully automatic without any user interaction 

### Usage:

* Create folder `scripts` in same location
* Add your script file(s) to `scipts` folder, only execute file with extension(s): `sh, bat, ps1`
* Run app: 
    * execute all script(s) with no timeout: `python script_execute.py`
    * execute all script(s) with timeout for 30 seconds: `python script_execute.py 30`
    * execute single script with no timeout: `python script_execute.py 0 my_script.sh`
* The output logs will save in `logs` folder

### Build app:

* With _make_: `make build_exe`
* (or): `pyinstaller --onefile script_execute.py`