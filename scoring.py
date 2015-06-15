import math
import operator as op
import functools as ft
from stories import datasets

WINMULT = 3
SLEN = 10
CRFIDF = 0

def corefify(tokens, alt, stopwords=False):
    
    def sw(x):
        return x["coreference"] or stopwords or not x["stopword"]
    def nscrf(x):
        return not x["subcoref"]

    return reduce(list.__add__,[crf(alt,t) if t["coreference"] else [t]
                                for t in filter(sw,filter(nscrf,tokens))])

def crf(alt, t):

    return [{alt:{"word":c["word"],
                  "idf":(t["origidf"] if CRFIDF else c["idf"])},
             "matches":{
                ("q"+alt):map(op.itemgetter(c["word"]),
                              t["matches"]["qcoref"]),
                ("a"+alt):map(op.itemgetter(c["word"]),
                              t["matches"]["acoref"])}}
            for c in t["coreference"]]

def hypify(tokens, q, a):

    return [h["idf"] for h,t in zip(map(op.itemgetter("hypernym"),tokens),tokens)
            if t["qhypmatches"][q] or t["ahypmatches"][q][a]]

def sel(x, y):

    return x[y]

def nestacc(l, d):

    return reduce(sel,l,d)

def nest(l):

    return ft.partial(nestacc,l)

def score(stories, scoref, word="token", coref=False,
          stopwords=True, negation=False, hypernymy=False, categorise=False):

    def sw(x):
        return stopwords or not x["stopword"]

    sc = []
 
    for story in stories:

        s = [0.0 for _ in range(16)]

        coreftoks = corefify(story["tokens"],word,stopwords=stopwords)
        toks = filter(sw,story["tokens"])
        
        if not categorise and coref:
            s = map(ft.partial(op.mul,1.0),
                    scoretoks(coreftoks,[],story,scoref,
                              word,negation,hypernymy,categorise))
        elif not categorise:
            s = map(op.add,scoretoks(toks,[],story,scoref,
                                     word,negation,hypernymy,categorise),s)
        else:
            s = map(op.add,scoretoks(toks,coreftoks,story,scoref,
                                     word,negation,hypernymy,categorise),s)
            
        sc.extend(s)

    return sc


def scoretoks(toks, coreftoks, story, scoref, word,
              negation, hypernymy, categorise):

    sc = []
    
    for i in range(4):

        sc.extend([0.0 for _ in range(4)])
        
        if categorise and all([categories[c] for c in story["categories"][i]]):
            sc[-4:] = scoreq(coreftoks,i,story,scoref,word,negation,hypernymy)

        sc[-4:] = map(op.add,scoreq(toks,i,story,scoref,
                                    word,negation,hypernymy),sc[-4:])

    return sc

def scoreq(ts, i, story, scoref, word, negation, hypernymy):

    def frq(x,y,z):
        return (x or y) * z;

    sc = []
    
    freqs = map(nest([word,"idf"]),ts)
    
    qmt = map(nest(["matches","q"+word]),ts)
    amt = map(nest(["matches","a"+word]),ts)
    
    q = map(op.itemgetter(i),qmt)
    a = map(op.itemgetter(i),amt)
    
    if negation:
        
        if story["negativeqs"][i]:
                    
            asc = [sum(map(op.itemgetter(j),a))
                   for j in range(4)]
                    
            if not min(asc) and len([1 for x in asc if x == min(asc)]) < 2:
                return map(op.not_,asc)
            
    for j in range(4):
                
        an = map(op.itemgetter(j),a)
        s = scoref(map(frq,q,an,freqs),story,i,j,q,an)
        
        if hypernymy:

            s += scoref(hypify(story["tokens"],i,j),
                        story,i,j,q,an) * 1.0
                    
        sc.append(s)

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

    winlen = int(SLEN * WINMULT)

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

def avgsentlen(stories):
    
    slens = [len(story["tokens"]) / len(story["sentenceoffsets"])
             for story in stories]

    return sum(slens) / len(slens)

def splitevery(n, l):

    for i in range(0,len(l),n):
        yield l[i:i+n]

def grade(scores, answers, result=True):
    
    def top(x):
        return [s == max(x) for s in x]

    grades = [1.0 / len(filter(op.truth,s)) if sum(map(op.mul,a,s)) else 0.0
              for s,a in zip(map(top,splitevery(4,scores)),answers)]
    
    return (sum(grades) * 1.0 / len(grades)) if result else grades

def scoreset(stories, answers, rtescores, settype, flags, result=True):

    allscores = []

    for scoref in scorefs:

        if scoref != rte:
            scores = score(stories,scoref,**flags[scoref])
        else:
            scores = rtescores
            
        allscores.append([s * scorefs[scoref][settype + "weight"]
                          for s in scores])
 
    return grade(map(sum,zip(*allscores)),answers,result)


def scorewithflags(devtest, flags, rte=False, result=False):
 
    return {l:{n:scoreset(s["stories"],
                          s["answers"],
                          s["rtescores"] if rte else fakerte(s["stories"]),
                          s["settype"],
                          f,result=result)
               for n,s in datasets[devtest].items()}
            for l,f in flags.items()}

def fakerte(stories):
    
    return [0.0 for _ in range(len(stories) * 16)]

def getflags(flags):

    default = {scoref:dict(scorefs[scoref]["args"]) for scoref in scorefs}

    for f,v in flags.items():
        for scoref in default:
            default[scoref][f] = v

    return default
            
def scoredevtrain(verbose=False):

    if verbose:
        flags = {"base":getflags({"word":"token","negation":False,
                                  "categorise":False}),
                 "1neg":getflags({"word":"token","categorise":False}),
                 "2stem":getflags({"negation":False,"categorise":False}),
                 "3coref":getflags({"negation":False}),
                 "4best":getflags({})}
    else:
        flags = {"coref":getflags({"coref":True,"categorise":False}),
                 "norules":getflags({"categorise":False,"negation":False}),
                 "best":getflags({})}

    return scorewithflags("devtrain",flags)

def windowscores():

    global WINMULT

    oldwm = WINMULT
    winscores = dict()

    for i in range(1,5):

        WINMULT = i

        flags = {"best":getflags({}),
                 "norules":getflags({"categorise":False})}

        winscores[i] = scorewithflags("devtrain",flags)

    WINMULT = oldwm

    return winscores

def testscores():

    return {"rte":scorewithflags("test",{"norules":getflags({"categorise":False}),
                                         "rules":getflags({})},rte=True),
            "norte":scorewithflags("test",{"rules":getflags({}),
                                           "norules":getflags(
                                               {"categorise":False})})}
    

scorefs = {distance:{"mc160weight":10,
                     "mc500weight":11,
                     "args":dict(word="token",
                                 coref=False,
                                 stopwords=False,
                                 negation=True,
                                 hypernymy=False,
                                 categorise=False)
                     },
           
           impslidingwindow:{"mc160weight":1,
                             "mc500weight":1,
                             "args":dict(word="lemma",
                                         coref=False,
                                         stopwords=True,
                                         negation=True,
                                         hypernymy=False,
                                         categorise=True)
                             },
           
           bowall:{"mc160weight":1,
                   "mc500weight":6,
                   "args":dict(word="token",
                               coref=False,
                               stopwords=False,
                               negation=True,
                               hypernymy=False,
                               categorise=True)
                   },
           
           rte:{"mc160weight":40,
                "mc500weight":25,
                "args":dict()
                },
           
           }

categories = {"what":True,
              "did/do":False,
              "multiple sentences":False,
              "neg":False,
              "who":False,
              "when":False,
              "CD":True,
              "how":False,
              "OTHER":False,
              "tmod":False,
              "which":True,
              "where":True,
              "why":False,
              "whose":False}
