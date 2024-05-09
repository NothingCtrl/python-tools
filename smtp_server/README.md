# Simple SMTP Server

Create a simple SMTP server listen on port `25` then send email to a production SMTP server with authentication required

Before run, create a `.env` file follow example: `.env_example`

### Usage

* Run test: `python simple_smtp_server.py smtp-test`
* Run server forever `python simple_smtp_server.py`


### Release

* The release file `release/simple_smtp_server.exe` build with `pyinstaller` on Windows 11 64bit 