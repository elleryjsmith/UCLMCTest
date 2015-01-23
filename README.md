# UCLMCTest


Basic MCTest system, uses lemmatization and bag-of-words matching

Includes basic Python interface between the Stanford Parser and MCTest stories



Requires:

jython 2.5.3
JDK 8

Stanford Parser .jars:

https://dl.dropboxusercontent.com/s/irqldm5553vhswr/stanford-parser.jar

https://dl.dropboxusercontent.com/s/y8xvj42aabajauz/stanford-parser-3.5.0-models.jar


Usage:

jython -Dpython.path=stanford-parser.jar:stanford-parser-3.5.0-models.jar baseline.py > out.txt

