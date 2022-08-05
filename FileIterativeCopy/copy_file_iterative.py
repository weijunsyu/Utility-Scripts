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
import argparse
import shutil
import math


def IsValidDirectory(path):
    return os.path.isdir(path)

def GetNumber(string, stripAlpha=False, stripSpecial=False):
    if stripAlpha:
        string = "".join(filter(lambda x: not x.isalpha(), string))
    if stripSpecial:
        string = "".join(filter(lambda x: x.isalnum(), string))

    if string.isdigit():
        return int(string)
    else:
        return math.nan

def GetFilename(filepath, extension=False):
    filename = os.path.split(filepath)[1]
    if not extension:
        filename = os.path.splitext(filename)[0]
    return filename

def SplitFilepath(filepath):
    dir, name_ext = os.path.split(filepath)
    name, ext = os.path.splitext(name_ext)
    return dir, name, ext

def GetDirname(dirpath):
    return os.path.basename(dirpath)

def GetPathList(source, directory=False, shallow=True):
    pathList = []
    for root, dirs, files in os.walk(source):
        if directory:
            for dir in dirs:
                dirpath = os.path.join(root, dir)
                pathList.append(dirpath)
        else:
            for file in files:
                filepath = os.path.join(root, file)
                pathList.append(filepath)
        if shallow:
            break
    return pathList

def SortPathList(pathList, directory=False):
    def sortKey(path):
        string = GetFilename(path, extension=False)
        if directory:
            string = GetDirname(path)
        return GetNumber(string, stripAlpha=True, stripSpecial=True)

    return sorted(pathList, key=sortKey)

def DoIterativeMerge(dest, sourceList, initial, counter, prefix, suffix, override, verbose=False, quiet=False):
    for source in sourceList:
        if not quiet:
            print("Now sorting files in: '" + source + "'")
        paths = SortPathList(GetPathList(source, directory=False, shallow=True), directory=False)
        if not quiet:
            print("Now copying files from: '" + source + "' to: '" + dest + "'")
        for path in paths:
            dir, name, ext = SplitFilepath(path)
            sourceName = os.path.join(dir, name + ext)

            destNameCounter = prefix + str(initial) + suffix
            destName = ""
            if override:
                destName = os.path.join(dest, destNameCounter + ext)
            else:
                destName = os.path.join(dest, name + destNameCounter + ext)

            shutil.copy(sourceName, destName)
            if verbose:
                print("Copied '" + sourceName + "' to '" + destName + "'")

            initial += counter

def DoBulkMerge(dest, source, initial, counter, prefix, suffix, override, verbose=False, quiet=False):
    if not quiet:
        print("Now sorting subdirectories in: '" + source + "'")
    sortedDirs = SortPathList(GetPathList(source, directory=True, shallow=True), directory=True)
    if verbose:
        print("Sorted subdirectories in order are as follows:")
        for dir in sortedDirs:
            print(dir)
    DoIterativeMerge(dest, sortedDirs, initial=initial, counter=counter, prefix=prefix, suffix=suffix, override=override, verbose=verbose, quiet=quiet)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy files from all source directories such that files in the destination are numbered in consecutive order. Options for new filename can be set by the user. Files and directories are sorted by name, ignoring any non-numeric characters. Shallow copy only such that subdirectories will not be traversed.")
    parser.add_argument("dest", type=str, metavar="destination", help="Path to the destination directory.")
    sourceGroup = parser.add_mutually_exclusive_group(required=True)
    sourceGroup.add_argument("-s", "--source", action="append", type=str, help="Path to the source directory holding files to be copied to destination. Each extra argument will add another source directory to the list of directories holding source files.")
    sourceGroup.add_argument("-b", "--bulk", type=str, help="Path to the directory holding subdirectories of source files that will be copied over to destination.")
    parser.add_argument("-i", "--initial", type=int, nargs="?", const=0, default=0, help="Set the initial value of the file counter. Default=0")
    parser.add_argument("-c", "--counter", type=int, nargs="?", const=1, default=1, help="Set the counter step value. Default=1")
    parser.add_argument("-p", "--prefix", type=str, default="", help="Optional prefix to attach to the counter.")
    parser.add_argument("-u", "--suffix", type=str, default="", help="Optional suffix to attach to the counter.")
    parser.add_argument("-o", "--override", action="store_true", help="Overrides the old filename such that the old name is dropped after the operation.")
    logGroup = parser.add_mutually_exclusive_group()
    logGroup.add_argument("-v", "--verbose", action="store_true", help="Output actions to the console and show detailed information.")
    logGroup.add_argument("-q", "--quiet", action="store_true", help="Suppress ouptut to the console.")

    args = parser.parse_args()

    if args.source:
        quitFlag = False
        for source in args.source:
            if not IsValidDirectory(source):
                quitFlag = True
                if args.verbose:
                    print("The source path: '" + source + "'" + " is an invalid directory.")
                elif not args.quiet:
                    print("Some source path(s) are invalid.")
                    sys.exit()
                else:
                    sys.exit()
        if quitFlag:
            sys.exit()

    elif not IsValidDirectory(args.bulk):
        if args.verbose:
            print("The destination path: '" + args.bulk + "'" + " is an invalid directory.")
        elif not args.quiet:
            print("Destination path is invalid.")
        sys.exit()

    if not IsValidDirectory(args.dest):
        if not args.quiet:
            print("The destination path does not exist. Creating directory...")
        try:
            os.makedirs(args.dest)
            if args.verbose:
                print("Created destination directory: " + "'" + args.dest + "'")
        except OSError as error:
            if args.verbose:
                print("Failed to create destination directory: '" + args.dest + "'")
            elif not args.quiet:
                print("Failed to create destination directory.")
            sys.exit()

    if not args.quiet:
        print("Starting operation...")

    if args.source:
        DoIterativeMerge(args.dest, args.source, args.initial, args.counter, args.prefix, args.suffix, args.override, args.verbose, args.quiet)
    elif args.bulk:
        DoBulkMerge(args.dest, args.bulk, args.initial, args.counter, args.prefix, args.suffix, args.override, args.verbose, args.quiet)

    if not args.quiet:
        print("Finished copying files.")
        sys.exit()
