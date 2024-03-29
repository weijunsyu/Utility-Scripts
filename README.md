# Utility Scripts

Collection of scripts for performing utility tasks. Mostly CLI programs primarily targeted at Windows OS.

1. **FolderNameToFileRename**  
Rename files from all source directories such that their new name is the same as their immediate directory name. Options for duplicate new filenames can be set by the user. By default a shallow traversal of source directories is performed.
    - language: python3
    - target: cross-platform
    - type: CLI script
    - dependencies: none


2. **FolderSync**  
Merge/Mirror/Copy one-way or two-way between source and destination (their subdirectories and files). Additionally, allows for continuous syncing of source and destination one-way or two-way.
    - language: python3
    - target: Windows
    - type: CLI script
    - dependencies:
        - watchdog

3. **IterativeFileCopy**  
Copy files from all source directories such that files in the destination are numbered in consecutive order. Options for new filename can be set by the user. Files and directories are sorted by name, ignoring any non-numeric characters. Shallow copy only such that subdirectories will not be traversed.
    - language: python3
    - target: cross-platform
    - type: CLI script
    - dependencies: none
