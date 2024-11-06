# MIT License
#
# Copyright (c) 2022 WeiJun Syu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import os
import subprocess
import time
import logging
import argparse
import shutil
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler


ROBOCOPY_SILENT_FLAGS = " /NFL /NDL /NJH /NJS /nc /ns /np"


def IsWindows():
    if os.name == "nt":
        return True
    return False

def IsLinux():
    if os.name == "posix":
        return True
    return False

def NormalizePath(path):
    return os.path.normpath(path)

def IsValidDirectory(path):
    return os.path.isdir(path)

def SplitPathByMatch(path, prefix=None, suffix=None):
    if prefix:
        try:
            path = path.removeprefix(prefix)
        except:
            if path.startswith(prefix):
                path = path[len(prefix):]
    if suffix:
        try:
            path = path.removesuffix(suffix)
        except:
            if path.endswith(suffix):
                path = path[:-len(suffix)]
    return path

def RemoveBoundingPathSeperators(path, leading=True, trailing=True):
    if leading and trailing:
        return path.strip(os.sep)
    elif leading:
        return path.lstrip(os.sep)
    elif trailing:
        return path.rstrip(os.sep)

def DoMerge(source, dest, twoway, verbose=False, python=False):
    # Copy all files that share the same filename and skipping all other files
    for root, dirs, files in os.walk(source):
        for file in files:
            commonRoot = RemoveBoundingPathSeperators(SplitPathByMatch(root, source))
            sourceName = os.path.join(root, file)
            destName = os.path.join(dest, commonRoot, file)
            # if file exists in destination
            if os.path.exists(destName):
                appendValue = 1
                while True:
                    # seperate the extension from the filename
                    base, ext = os.path.splitext(file)
                    # append number to filename without extension and update path
                    destName = os.path.join(dest, commonRoot, base + "_" + str(appendValue) + ext)
                    # if new, number appended filename, doesnt exist then move file
                    if not os.path.exists(destName):
                        shutil.copy(sourceName, destName)
                        if verbose:
                            print("Copied '" + sourceName + "' to '" + destName + "'")
                        break
                    appendValue += 1
    # Copy all files from source to dest that do not share the same filename
    if python:
        print("Not yet implemented.")
    elif IsWindows():
        flags = " /COPY:DAT /DCOPY:T /E /Z /J /W:5 /XO /XN /XC"
        batString = "Robocopy \"" + source + "\" \"" + dest + "\"" + flags
        if not verbose:
            batString += ROBOCOPY_SILENT_FLAGS
            subprocess.run(batString, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) #run .bat process
        subprocess.run(batString)
    elif IsLinux():
        print("Not yet implemented.")

    if twoway:
        DoMirror(source, dest, False, False)

def DoMirror(source, dest, modTime, twoway, verbose=False, python=False):
    def DoMirror(source, dest, modTime):
        if python:
            print("Not yet implemented.")
        elif IsWindows():
            flags = " /MIR /E /Z /J /IT /IS /W:5" # Mirror source to dest in restartable mode with 5s wait delay on retry
            if modTime:
                flags += " /XO" # XO specifies that if the file in source is older than the file in dest it will NOT be copied
            batString = "Robocopy \"" + source + "\" \"" + dest + "\"" + flags
            if not verbose:
                batString += ROBOCOPY_SILENT_FLAGS
                subprocess.run(batString, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) #run .bat process
            else:
                subprocess.run(batString)
        elif IsLinux():
            print("Not yet implemented.")

    DoMirror(source, dest, modTime)
    if twoway:
        DoMirror(dest, source, modTime)

def DoCopy(source, dest, modTime, twoway, verbose=False, python=False):
    def DoCopy(source, dest, modTime):
        if python:
            print("Not yet implemented.")
        elif IsWindows():
            flags = " /COPY:DAT /DCOPY:T /E /Z /J /IT /IS /W:5"
            if modTime:
                flags += " /XO"
            batString = "Robocopy \"" + source + "\" \"" + dest + "\"" + flags
            if not verbose:
                batString += ROBOCOPY_SILENT_FLAGS
                subprocess.run(batString, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) #run .bat process
            else:
                subprocess.run(batString)
        elif IsLinux():
            print("Not yet implemented.")

    DoCopy(source, dest, modTime)
    if twoway:
        DoCopy(dest, source, modTime)

def InitMonitor(source, dest, modTime, funcOnEvent, python=False):
    class SyncEventHandler(LoggingEventHandler):
        def on_any_event(self, event):
            funcOnEvent(source, dest, modTime, False, python)

    syncEventHandler = SyncEventHandler()
    observer = Observer()
    observer.schedule(syncEventHandler, source, recursive=True)
    observer.start()
    return observer

def InitLogger():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

def StartSyncing(source, dest, observers, twoway=False, quiet=False):
    print("Now Syncing from '" + source + "' to '" + dest + "'")
    if twoway:
        print("And Syncing from '" + dest + "' to '" + source + "'")
    if not quiet:
        print("Press Ctrl + C to terminate program.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for observer in observers:
            observer.stop()
    for observer in observers:
        observer.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge/Mirror/Copy one-way or two-way between source and destination (their subdirectories and files). Additionally, allows for continuous syncing of source and destination one-way or two-way. This program uses subprocess and Robocopy to perform operations on the Windows platform.")
    parser.add_argument("source", type=str, help="Path to the source directory.")
    parser.add_argument("dest", type=str, metavar="destination", help="Path to the destination directory.")
    modeGroup = parser.add_mutually_exclusive_group()
    modeGroup.add_argument("-m", "--merge", action="store_true",
                           help="Merge source into destination preserving any files found unique to destination. Files that share a name but differ in content will be appended a number to preserve uniqueness. Ex. original_filename, original_filename_1, original_filename_2, ... , original_filename_6, ...")
    modeGroup.add_argument("-c", "--copy", action="store_true",
                           help="Copy source into destination preserving any files found unique to destination. Files that share a name will be overwritten (by the file in source).")
    modeGroup.add_argument("-i", "--mirror", action="store_true",
                           help="Mirror source into destination purging any files found unique to destination. Files that share a name will be overwritten (by the file in source).")
    contGroup = parser.add_mutually_exclusive_group()
    contGroup.add_argument("-s", "--sync", action="store_true",
                           help="Perform continuous symmetrical mirror syncing (two-way mirror) of the two directories such that they are kept identical. Conflicts are resolved such that the source to destination direction takes precedence. Performed after initial merge/mirror/copy action. Not affected by the twoway argument.")
    contGroup.add_argument("-a", "--asymc", action="store_true",
                           help="Perform continuous asymmetrical copy syncing (one-way copy) of source to destination. Performed after initial merge/mirror/copy action. Not affected by the twoway argument.")
    contGroup.add_argument("-y", "--asymi", action="store_true",
                           help="Perform continuous asymmetrical mirror syncing (one-way mirror) of source to destination. Performed after initial merge/mirror/copy action. Not affected by the twoway argument.")
    parser.add_argument("-t", "--time", dest="modTime", action="store_true",
                        help="Prevent overwriting files if the file to be overwritten has a more recent date of modification. Does not guarantee file safety as not all actions performed on files modify their timestamp depending on the OS.")
    parser.add_argument("-w", "--twoway", action="store_true",
                        help="Perform the initial merge/copy/mirror action bi-directionally. Conflicts are resolved such that the source to destination direction takes precedence.")
    parser.add_argument("-p", "--python", action="store_true",
                        help="Perform actions with a purely python implementation within current process.")
    logGroup = parser.add_mutually_exclusive_group()
    logGroup.add_argument("-v", "--verbose", action="store_true",
                          help="Output actions to the console and show detailed information.")
    logGroup.add_argument("-q", "--quiet", action="store_true",
                          help="Do not ask for user confirmation on action and limit console interaction.")

    args = parser.parse_args()

    if not args.merge and not args.copy and not args.mirror and not args.sync and not args.asymc and not args.asymi:
        if not args.quiet:
            input("Please choose at least one option to perform. [-m | -c | -i | -s | -a | -y]")
        sys.exit()

    args.source = NormalizePath(args.source)
    args.dest = NormalizePath(args.dest)

    if not IsValidDirectory(args.source):
        if args.verbose:
            print("'" + args.source + "'" + " is an invalid directory.")
            if not args.quiet: # verbose and not quiet
                input("Press ENTER to terminate the program.")
        elif not args.quiet: # not verbose and not quiet
            input("Source path invaild. Press ENTER to terminate the program.")
        sys.exit()

    if not IsValidDirectory(args.dest):
        try:
            os.makedirs(args.dest)
            if args.verbose:
                print("Created directory: " + "'" + args.dest + "'")
        except OSError as error:
            if args.verbose:
                print("Failed creating directory: '" + args.dest + "'")
                if not args.quiet: # verbose and not quiet
                    input("Press ENTER to terminate the program.")
            elif not args.quiet: # not verbose and not quiet
                input("Destination path cannot be created. Press ENTER to terminate the program.")
            sys.exit()


    if args.merge:
        DoMerge(args.source, args.dest, args.twoway, args.verbose, args.python)
    elif args.copy:
        DoCopy(args.source, args.dest, args.modTime, args.twoway, args.verbose, args.python)
    elif args.mirror:
        DoMirror(args.source, args.dest, args.modTime, args.twoway, args.verbose, args.python)

    if args.sync or args.asymc or args.asymi:
        InitLogger()
        observers = []
        if args.sync:
            sourceObserver = InitMonitor(args.source, args.dest, args.modTime, DoMirror, args.python)
            destObserver = InitMonitor(args.dest, args.source, args.modTime, DoMirror, args.python)
            observers.append(sourceObserver)
            observers.append(destObserver)
        elif args.asymc:
            sourceObserver = InitMonitor(args.source, args.dest, args.modTime, DoCopy, args.python)
            observers.append(sourceObserver)
        elif args.asymi:
            sourceObserver = InitMonitor(args.source, args.dest, args.modTime, DoMirror, args.python)
            observers.append(sourceObserver)

        StartSyncing(args.source, args.dest, observers, args.twoway, args.quiet)
        if not args.quiet:
            print("Program terminated by user.")
        sys.exit()
