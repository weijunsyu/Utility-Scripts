@echo off

REM MIT License
REM
REM Copyright (c) 2024 WeiJun Syu
REM
REM Permission is hereby granted, free of charge, to any person obtaining a copy
REM of this software and associated documentation files (the "Software"), to deal
REM in the Software without restriction, including without limitation the rights
REM to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
REM copies of the Software, and to permit persons to whom the Software is
REM furnished to do so, subject to the following conditions:
REM
REM The above copyright notice and this permission notice shall be included in all
REM copies or substantial portions of the Software.
REM
REM THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
REM IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
REM FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
REM AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
REM LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
REM OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
REM SOFTWARE.

setlocal ENABLEDELAYEDEXPANSION

if not "%~1"=="" (
    if not "%~2"=="" (
        if not "%~3"=="" (
            echo Incorrect number of arguments.
            echo.
            goto help
        )
        goto start
    )
)

:help
echo Usage: batchfilename.bat "folderpath" "outputfile"
echo.
echo Example: batchfilename "C:\Myfolder" "output"
echo.
echo This script will copy the file name and extension of each file in the specified folder to a text file.
echo If the output file already exists, a unique file name will be generated.
echo NOTE: The 'outputfile' argument does not contain the file extension. The file extension will always be '.txt' which will be appended automatically.
exit /b

:start
set "folder=%~1"
set "filename=%~2"
set "base=%filename%"

if not exist "%folder%" (
    echo Folder does not exist.
    exit /b 1
)

set "ext=.txt"
set "count=2"

if not exist "%filename%%ext%" (
    set "filename=%filename%%ext%"
    goto generate
)

:loop
if exist "%filename%(%count%)%ext%" (
    set /a count+=1
    goto loop
)

set "filename=%filename%(%count%)%ext%"

:generate
for %%f in ("%folder%\*.*") do (
    echo %%~nf%%~xf>>"%filename%"
)

echo File names written to "%filename%".

exit /b 0