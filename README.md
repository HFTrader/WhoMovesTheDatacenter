# WhoMovesTheDatacenter
Quick assessment of what languages move the datacenter

* Methodology

We focus on Ubuntu 16.04 server. A server this type is represented by the top package "ubuntu-server". 

From this package we derive its dependencies recursively, taking into account repetition and recursion, if exists.

Packages keep a count of the number of references are made to them, directly or indirectly.

Each package source is then downloaded and every file inside it is classified with the 'file' utility. 

Types are further grouped to conflate related groups as "C source, UTF-8" and "C source, ASCII" for example.

We count how many lines, words, bytes each file contains and update this contribution to its group.

The number of package references is grandfathered to each individual file it contains.

The end result is a map of File Type into statistics (lines,words,bytes,direct references,indirect references).

Map is sorted by number of lines and printed in CSV format.

Usage: 

    python list_dependencies.py ubuntu-server > results.txt 

