# UCLMCTest


Basic MCTest system, uses lemmatization and bag-of-words matching

Includes basic Python interface between the Stanford Parser and MCTest stories

## To set up

### Set up python

```
$ pip install nltk numpy scipy
$ python
  import nltk
  nltk.download()
# Install all-corpora
```

### TODO How to set up Jython and produce the parse trees with Stanford Parser

Stanford Parser .jars:
```
$ wget https://dl.dropboxusercontent.com/s/irqldm5553vhswr/stanford-parser.jar
$ wget https://dl.dropboxusercontent.com/s/y8xvj42aabajauz/stanford-parser-3.5.0-models.jar
```


Usage:

jython -Dpython.path=stanford-parser.jar:stanford-parser-3.5.0-models.jar baseline.py > out.txt

