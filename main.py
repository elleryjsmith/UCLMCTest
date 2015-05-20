import json
import sys
import csv
import math
import operator as op
import functools as ft
import cPickle as pickle

def ans(dataset):

    def corr(x):
        return [1 if i == ord(x) - 0x41 else 0 for i in range(4)]

    with open("datasets/" + dataset + ".ans","r") as fl:     
        return map(corr,reduce(list.__add__,csv.reader(fl,delimiter='\t')))

def corefify(tokens, alt, stopwords=False):
    
    def sw(x):
        return x["coreference"] or stopwords or not x["stopword"]
    def nscrf(x):
        return not x["subcoref"]

    return reduce(list.__add__,[crf(alt,t) if t["coreference"] else [t]
                                for t in filter(sw,filter(nscrf,tokens))])

def crf(alt, t):

    return [{alt:c,"matches":{
                ("q"+alt):map(op.itemgetter(c["word"]),
                              t["matches"]["qcoref"]),
                ("a"+alt):map(op.itemgetter(c["word"]),
                              t["matches"]["acoref"])}}
            for c in t["coreference"]]

def sel(x, y):

    return x[y]

def nestacc(l, d):

    return reduce(sel,l,d)

def nest(l):

    return ft.partial(nestacc,l)

def score(stories, scoref, word="token", coref=False, stopwords=True):

    def sw(x):
        return stopwords or not x["stopword"]
    def frq(x,y,z):
        return (x or y) * z;

    sc = []
 
    for story in stories:

        if coref:
            toks = corefify(story["tokens"],word,stopwords=stopwords)
        else:
            toks = filter(sw,story["tokens"])
        
        freqs = map(nest([word,"idf"]),toks)
        
        qmt = map(nest(["matches","q"+word]),toks)
        amt = map(nest(["matches","a"+word]),toks)
        
        for i,_ in enumerate(qmt[0]):

            q = map(op.itemgetter(i),qmt)
            a = map(op.itemgetter(i),amt)
            
            if story["negativeqs"][i]:
                asc = [sum(map(op.itemgetter(j),a))
                       for j,_ in enumerate(amt[i][0])]
                if not min(asc) and len([1 for x in asc if x == min(asc)]) < 2:
                    sc.extend(map(op.not_,asc))
                    continue
            
            for j,_ in enumerate(amt[i][0]):
                an = map(op.itemgetter(j),a)
                sc.append(scoref(map(frq,q,an,freqs),story,i,j,q,an))

    return sc

def slidingwindow(matches, story, q, a, qm, am):
    
    winlen = (story["qalengths"][q]["question"] + 
              story["qalengths"][q]["answers"][a])

    if winlen > len(matches):
        return sum(matches)
    else:
        return max([sum(matches[i:i+winlen])
                    for i in range(0,len(matches)-winlen)] + [0])


def impslidingwindow(matches, story, q, a, qm, am):

    winlen = 30

    if winlen > len(matches):
        return sum(matches)
    else:
        return sum([max([sum(matches[i:i+w]) 
                         for i in range(0,len(matches) - w)] + [0])
                    for w in range(2,winlen)])

def fst(t):

    return t[0]

def snd(t):

    return t[1]

def distance(matches, story, q, a, qm, am):

    if not (sum(qm) and sum(am)):
        return -1.0

    qoccs = map(fst,filter(snd,enumerate(qm)))
    aoccs = map(fst,filter(snd,enumerate(am)))
    
    dist = [min([abs(o - n) + 1 for n in aoccs]) for o in qoccs]
    d = sum(dist) * 1.0 / len(dist)

    return -((1.0 / (len(matches) - 1)) * d)

def bowall(matches, story, q, a, qm, am):

    return sum(matches)

def rte():
    
    pass

def splitevery(n, l):

    for i in range(0,len(l),n):
        yield l[i:i+n]

def grade(scores, answers):
    
    def top(x):
        return [s == max(x) for s in x]

    grades = [1.0 / len(filter(op.truth,s)) if sum(map(op.mul,a,s)) else 0.0
              for s,a in zip(map(top,splitevery(4,scores)),answers)]
    
    return (sum(grades) * 1.0 / len(grades))

def scoreall(stories, answers, rtescores, settype):

    rteweight = scorefs[rte][settype + "weight"]
    scorefs[rte][settype + "weight"] = 0

    for scoref in scorefs:
        scorefs[scoref]["args"]["coref"] = True
    withcoref = scoreset(stories, answers, rtescores, settype)

    for scoref in scorefs:
        scorefs[scoref]["args"]["coref"] = False
    nocoref = scoreset(stories, answers, rtescores, settype)

    scorefs[rte][settype + "weight"] = rteweight
    withrte = scoreset(stories, answers, rtescores, settype)

    return (nocoref,withcoref,withrte)

def scoreset(stories, answers, rtescores, settype):

    allscores = []

    for scoref in scorefs:

        if scoref != rte:
            scores = score(stories,scoref,**scorefs[scoref]["args"])
        else:
            scores = rtescores
            
        allscores.append([s * scorefs[scoref][settype + "weight"]
                          for s in scores])
 
    return grade(map(sum,zip(*allscores)),answers)

def loadstories(dataset):

    with open("datasets/" + dataset + ".json","r") as fl:
        return json.load(fl)

def loadrte(dataset):    

    with open("datasets/" + dataset + ".rte","r") as fl:
        return pickle.load(fl)


scorefs = {distance:{"mc160weight":10,
                     "mc500weight":11,
                     "args":dict(word="token",
                                 coref=False,
                                 stopwords=False)
                     },
           
           impslidingwindow:{"mc160weight":1,
                             "mc500weight":1,
                             "args":dict(word="lemma",
                                         coref=False,
                                         stopwords=True)
                             },
           
           bowall:{"mc160weight":1,
                   "mc500weight":6,
                   "args":dict(word="token",
                               coref=False,
                               stopwords=False)
                   },
           
           rte:{"mc160weight":40,
                "mc500weight":25,
                "args":dict()
                },
           
           }

datasets = {"mc160devtrain":{"stories":(loadstories("mc160.dev") +
                                        loadstories("mc160.train")),
                             "answers":(ans("mc160.dev") +
                                        ans("mc160.train")),
                             "rtescores":(loadrte("mc160.dev") +
                                          loadrte("mc160.train")),
                             "settype":"mc160",
                             },
            "mc500devtrain":{"stories":(loadstories("mc500.dev") +
                                        loadstories("mc500.train")),
                             "answers":(ans("mc500.dev") +
                                        ans("mc500.train")),
                             "rtescores":(loadrte("mc500.dev") +
                                          loadrte("mc500.train")),
                             "settype":"mc500",
                             },
            "mc160test":{"stories":loadstories("mc160.test"),
                         "answers":ans("mc160.test"),
                         "rtescores":loadrte("mc160.test"),
                         "settype":"mc160",
                         },
            "mc500test":{"stories":loadstories("mc500.test"),
                         "answers":ans("mc500.test"),
                         "rtescores":loadrte("mc500.test"),
                         "settype":"mc500",
                         },
            }

if __name__ == "__main__":
    
    print "| Dataset | ImpSW+D | ImpSW+D+Coref | ImpSW+D+RTE |"

    for dataset,data in datasets.items():
        print "|",dataset,"| %f | %f | %f |" %scoreall(data["stories"],
                                                       data["answers"],
                                                       data["rtescores"],
                                                       data["settype"])

