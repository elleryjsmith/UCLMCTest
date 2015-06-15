import json
import sys
from nltk.corpus import wordnet as wn
from math import log

posmap = { "J": wn.ADJ,
           "N": wn.NOUN,
           "R": wn.ADV,
           "V": wn.VERB
           }

def stanwnpos(stanfordpos):

    if stanfordpos[:1] in posmap:
        return posmap[stanfordpos[:1]]
    else:
        return None

def loadstories(dataset):

    with open("datasets/" + dataset + ".json","r") as fl:
        return json.load(fl)

def wnlookup(word, pos):

    if not stanwnpos(pos):
        return None

    syn = wn.synsets(word,pos=stanwnpos(pos))
    hyp = syn[0].hypernyms() if syn else []

    for h in hyp:
        if "_" not in h.name():
            return h.name().split(".")[0]

    return None

def hyptokens(tokens):

    hypstory = [wnlookup(token["token"]["word"],token["pos"]) or
                token["token"]["word"] 
                for token in tokens]

    counts = {w:0.0 for w in hypstory}
    
    for w in hypstory:
        counts[w] += 1

    hypstory = [{"word":h,"idf":log(1 + (1 / (1 + counts[h])))}
                for h in hypstory]

    return hypstory

def addhyps(story):
    
    for t,h in zip(story["tokens"],hyptokens(story["tokens"])):
        t["hypernym"] = h

    hypmatches(story)
        
    return story

def hypmatches(story):

    for t in story["tokens"]:
    
        t["qhypmatches"] = [int(any([t["hypernym"]["word"] == w
                                     for w in (story["qlemmas"][i] +
                                               story["qtokens"][i])]))
                            for i in range(4)]

        t["ahypmatches"] = [[int(any([t["hypernym"]["word"] == w
                                      for w in (story["alemmas"][i][j] +
                                                story["atokens"][i][j])]))
                             for j in range(4)]
                            for i in range(4)]
        
if __name__ == "__main__":

    if not sys.argv[1:]:

        sys.stderr.write("Usage: python %s [dataset]\n" % (sys.argv[0]))
        exit()

    dataset = sys.argv[1]
    stories = loadstories(dataset)

    print " ".join([h["hypernym"]["word"] for h in addhyps(stories[0])["tokens"]])
    
    #with open("datasets/" + dataset + ".json","w") as fl:
    #    json.dump([addhyps(story) for story in stories],fl)
    
