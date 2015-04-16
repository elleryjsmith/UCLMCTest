from nltk.corpus import stopwords
from scoring import (bowall, negtokens, ild, ilpnd,
                     celev, sentselect, bow, selev)
from collections import OrderedDict as odict
from math import log

sw = set(stopwords.words("english"))

def baseline160(q,a,story):
    
    tokenize(q,a,story)
    lemmatize(q,a,story)
    coreference(q,a,story)
    hypernymy(q,a,story)
    stopwords(q,a,story)
    tokenfrequency(q,a,story)

def baseline500(q,a,story):

    tokenize(q,a,story)
    lemmatize(q,a,story)
    coreference(q,a,story)
    hypernymy(q,a,story)
    stopwords(q,a,story)
    #wordfrequency(q,a,story)

def settokens(story):
    
    for s in story.sentences:
        s.wbow = odict([(t,{}) for t in s.words])

def coreference(q,a,story):

    for s in story.sentences:
        for t in s.wbow:
            for c in t.coreference():
                s.wbow[t][c] = 1.0

def lemmatize(q,a,story):

    for s in story.sentences:
        for t in s.wbow:
            s.wbow[t][t.lemma] = 1.0

def tokenize(q,a,story):

    for s in story.sentences:
        for t in s.wbow:
            s.wbow[t][t.token.lower()] = 1.0
            
def tokencount(t,story):
    
    return t.frequency

wccache = dict()

def wordcount(w,story):
    
    if w not in wccache[story]:
        wccache[story][w] = len([1 for s in story.sentences for t in s.wbow
                                 if w in s.wbow[t]])

    return wccache[story][w]

def inversecount(i,story,fn):

    return log(1 + (1.0 / (fn(i,story) + 1)))

def wordfrequency(q,a,story):

    wccache[story] = dict()

    for s in story.sentences:
        for t in s.wbow:
            for w in s.wbow[t]:
                ic = inversecount(w,story,wordcount)
                s.wbow[t][w] *= ic

def tokenfrequency(q,a,story):

    for s in story.sentences:
        for t in s.wbow:
            for w in s.wbow[t]:
                s.wbow[t][w] *= inversecount(t,story,tokencount)
            
def stopwords(q,a,story):

    for s in story.sentences:
        for t in s.wbow:
            for w in s.wbow[t].copy():
                if w in sw:
                    del s.wbow[t][w]

def hypernymy(q,a,story):
    
    for s in story.sentences:
        for t in s.wbow:
            for h in t.hypernymy:
                s.wbow[t][h] = t.hypernymy[h]

def simplenegate(q,a,story):

    mnt = [(bowall(None,an,story),an) for an in q.answers]
    
    if len([m for m,an in mnt if not m]) == 1:
        for s in story.sentences:
            for t in s.wbow:
                s.wbow[t] = [(w.lemma,1.0) for w in min(mnt)[1].words]

def complexnegate(q,a,story):

    for w in [t for t in negtokens(q.qsentence)]:
        if w.parentclause():
            for s in story.sentences:
                for t in s.words:
                    if t.lemma in [y.lemma for y in w.parentclause().parsetree()]:
                        celev(s,t)

    return

    for s in story.sentences:
        for t in negtokens(s):
            ilpnd(s,[t])#ild(story,[t],"FB")

def propersubject(q):

    for d,r in q.parse.headword().dependents:
        if r == "nsubj" and d.isproper():
            return d

def subclauses(s):
    
    return [t for t in s.parse.parsetree() if t.isclausal() and t.pos != "S"]

def tempmods(s):

    return [d for g,d,r in s.parse.depgraph() if r == "tmod"]

def characterfocus(q,a,story):

    mc = propersubject(q.qsentence)

    for s in story.sentences:
        for t in s.wbow:
            if mc.lemma in t.coreference():
                celev(s,t)
                
def tempstory(q,a,story):
    
    for w in [t for t in q.qsentence.words
              if t.lemma == "before" or t.lemma == "after"]:
        if w.parentclause():
            for s in story.sentences:
                ild(story,[t for t in s.words
                           if t.lemma in
                           [y.lemma for y in w.parentclause().parsetree()]],
                    "B" if w.lemma=="before" else "F")


def whystory(q,a,story):

    for s in story.sentences:
        for t in s.wbow:
            if t.lemma == "because":
                ild(story,[t],"F")
