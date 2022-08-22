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


def IsValidDirectory(path):
    return os.path.isdir(path)

def GetImmediateDirectory(directoryPath):
    return os.path.basename(os.path.normpath(directoryPath))

def SplitFilepath(filepath):
    dir, name_ext = os.path.split(filepath)
    name, ext = os.path.splitext(name_ext)
    return dir, name, ext

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

def DoRename(sourceList, initial, counter, prefix, suffix, keep=False, shallow=True, verbose=False, quiet=False):
    for source in sourceList:
        if not quiet:
            print("Now renaming files in: '" + source + "'")
        pathlist = GetPathList(source, directory=False, shallow=shallow)
        for path in pathlist:
            dir, name, ext = SplitFilepath(path)
            
            newName = GetImmediateDirectory(dir)
            if keep:
                newName = name + " " + newName
            newPath = os.path.join(dir, newName + ext)

            renamed = False
            counterValue = initial
            while not renamed:
                try:
                    os.rename(path, newPath)
                     # if the above fails anything below wont be reached
                    if verbose:
                        print("Renamed '" + path + "' to '" + newPath + "'")
                    renamed = True
                except:
                    nameCounter = prefix + str(counterValue) + suffix
                    newPath = os.path.join(dir, newName + nameCounter + ext)
                    counterValue += counter

def DoBulkRename(source, initial, counter, prefix, suffix, keep=False, shallow=True, verbose=False, quiet=False):
    if not quiet:
        print("Now renaming subdirectories in: '" + source + "'")
    dirList = GetPathList(source, directory=True, shallow=True)
    if verbose:
        print("The list of subdirectories are as follows:")
        for dir in dirList:
            print(dir)
    DoRename(dirList, initial=initial, counter=counter, prefix=prefix, suffix=suffix, keep=keep, shallow=shallow, verbose=verbose, quiet=quiet)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename files from all source directories such that their new name is the same as their immediate directory name. Options for duplicate new filenames can be set by the user. By default a shallow traversal of source directories is performed.")
    sourceGroup = parser.add_mutually_exclusive_group(required=True)
    sourceGroup.add_argument("-s", "--source", action="append", type=str, help="Path to the source directory holding files to be renamed. Each extra argument will add another source directory to the list of directories holding source files.")
    sourceGroup.add_argument("-b", "--bulk", type=str, help="Path to the directory holding subdirectories of source files to be renamed. (Files in the root directory given will not be renamed.)")
    parser.add_argument("-i", "--initial", type=int, nargs="?", const=2, default=2, help="Set the initial value of the file counter. (Used to handle multiple files within the same directory.) Default=2")
    parser.add_argument("-c", "--counter", type=int, nargs="?", const=1, default=1, help="Set the counter step value. Default=1")
    parser.add_argument("-p", "--prefix", type=str, default="", help="Optional prefix to attach to the counter.")
    parser.add_argument("-u", "--suffix", type=str, default="", help="Optional suffix to attach to the counter.")
    parser.add_argument("-d", "--deep", action="store_true", help="Perform a deep traversal of source directories.")
    parser.add_argument("-k", "--keep", action="store_true", help="Keeps the old filename prepended to the new filename.")
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
            print("The source path: '" + args.bulk + "'" + " is an invalid directory.")
        elif not args.quiet:
            print("The source path is invalid.")
        sys.exit()

    if not args.quiet:
        print("Starting operation...")

    if args.source:
        DoRename(args.source, args.initial, args.counter, args.prefix, args.suffix, args.keep, not args.deep, args.verbose, args.quiet)
    elif args.bulk:
        DoBulkRename(args.bulk, args.initial, args.counter, args.prefix, args.suffix, args.keep, not args.deep, args.verbose, args.quiet)

    if not args.quiet:
        print("Finished renaming files.")
        sys.exit()
