## Script Execute

Using to execute all script file in `scripts` folder and get output

### Usage:

* Create folder `scripts` in same location
* Add your script file(s) to `scipts` folder, only execute file with extension(s): `sh, bat, ps1`
* Run app: 
    * run with no timeout: `python script_execute.py`
    * with timeout, example for 30 seconds: `python script_execute.py 30`
* The output logs will save in `logs` folder

### Build app:

* With _make_: `make build_exe`
* (or): `pyinstaller --onefile script_execute.py`