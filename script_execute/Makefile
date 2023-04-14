#!make
.PHONY: help start update stop destroy backup ssh
SHELL := /bin/bash

help:
	@echo ===================================================================================
	@echo usage:	"make <command>" to run target
	@echo ---
	@echo	help:		this help
	@echo	build_exe:	Build execute file
	@echo	build_exe_no_console:	Build execute file without console log
	@echo ===================================================================================
build_exe:
	@pyinstaller --onefile script_execute.py
build_exe_no_console:
	@pyinstaller --onefile --noconsole script_execute.py
all: help