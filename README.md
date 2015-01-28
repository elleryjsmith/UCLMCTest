# UCLMCTest

Improving on the MCTest

## To set up

```
$ pip install nltk numpy scipy
$ python
  import nltk
  nltk.download()
# Install all-corpora
```

## Test different features

```
$ python features/bow.py
```

## Parsing text MCTest datasets

We parse MCTest datasets with the Stanford parser.
To achieve the same results, do the following

- GetStanford Parser .jars:
```
$ wget https://dl.dropboxusercontent.com/s/irqldm5553vhswr/stanford-parser.jar
$ wget https://dl.dropboxusercontent.com/s/y8xvj42aabajauz/stanford-parser-3.5.0-models.jar
```
- Run the old baseline that creates a cache file
```
$ python hacks/baseline.py
```


Usage:

jython -Dpython.path=stanford-parser.jar:stanford-parser-3.5.0-models.jar baseline.py > out.txt

