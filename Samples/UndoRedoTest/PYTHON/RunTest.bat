@echo off
python ..\..\init.py
if %errorlevel% neq 0 exit /b %errorlevel%
set TEST_NAME=UndoRedoTest
python -u %TEST_NAME%.py
