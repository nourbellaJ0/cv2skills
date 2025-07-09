@echo off
python ..\..\init.py
if %errorlevel% neq 0 exit /b %errorlevel%
set TEST_NAME=InteractiveFormsTest
python -u %TEST_NAME%.py
