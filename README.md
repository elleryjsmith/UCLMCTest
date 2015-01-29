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

## Run it

Test different features
```
$ python features/bow.py
```

Test the classifier
```
$ python classifier.py
```

## Parsing text MCTest datasets

We parse MCTest datasets with the Stanford parser.
To achieve the same results, do the following

- GetStanford Parser .jars:
```
$ wget https://dl.dropboxusercontent.com/s/irqldm5553vhswr/stanford-parser.jar
$ wget https://dl.dropboxusercontent.com/s/y8xvj42aabajauz/stanford-parser-3.5.0-models.jar
```
- Run the parse cache that creates a cache file
```
jython -Dpython.path=stanford-parser.jar:stanford-parser-3.5.0-models.jar parsecache.py mc[160|500][dev|train]
```


