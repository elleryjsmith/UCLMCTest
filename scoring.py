from math import log
from collections import OrderedDict as odict

def weightedbow(s1,s2):

    return sum([wt for v in s1.values() for w,wt in v if w in set(s2)])

def qapair(q,a):
    
    return (q.qsentence.coreference if q else []) + (a.coreference if a else [])

def bow(q,a,story):

    return max([(weightedbow(s.wbow,qapair(q,a)),s) for s in story.sentences])

def bowall(q,a,story):

    return weightedbow(dict(reduce(lambda x,y:x+y.items(),
                                   [[]]+[s.wbow for s in story.sentences])),
                       qapair(q,a))

def slidingwindow(q,a,story):
    
    qa,ts = qapair(q,a),[]
    winlen = len(qa)

    for s in story.sentences:
        for t in s.wbow:
            if s.wbow[t]:
                ts.append((t,s.wbow[t]))

    if winlen >= len(ts):
        return bowall(q,a,story)
    else:
        return max([weightedbow(odict(ts[i:i+winlen]),qa)
                    for i in range(len(ts)-winlen)] + [0])

flg160 = True

def setflg(f):

    flg160 = f

def distance(q,a,story):

    qoccs,aoccs = [],[]
    qst = set(q.qsentence.coreference)
    ast = set(a.coreference) - qst

    i = 0
    for s in story.sentences:
        for t in s.wbow:
            ts = {t.lemma,t.token.lower()} if flg160 else set(map(lambda x:x[0],s.wbow[t]))
            if qst & ts:
                qoccs.append(i)
            if ast & ts:
                aoccs.append(i)
            i += 1

    if not (aoccs and qoccs):
        return 1.0


    dist = [min([abs(o - n) + 1 for n in aoccs]) for o in qoccs]
    d = sum(dist) * 1.0 / len(dist)

    return (1.0 / (i - 1)) * d

def swdistance(q,a,story):

    return (7 * slidingwindow(q,a,story)) - distance(q,a,story)
                        
def bowallnorep(q,a,story):

    seen,d = [],{0:[]}
    for s in story.sentences:
        for w,wt in [r for v in s.wbow.values() for r in v]:
            if w not in seen:
                seen.append(w)
                d[0].append((w,wt))

    return weightedbow(d,qapair(q,a))

def celev(s,c):

    if not c.isclausal():
        c = c.parentclause() or c.root()

    for t in c.parsetree():
        if t.isword():
            s.wbow[t] = [(w,wt*log(len(s.words))) for w,wt in s.wbow[t]]

def selev(s,k):

    for t in s.wbow:
        s.wbow[t] = [(w,wt*k) for w,wt in s.wbow[t]]

def sentselect(q,a,story):

    m = bow(q,a,story)[1]

    for s in story.sentences:
        if s != m:
            for t in s.wbow:
                s.wbow[t] = []

def ild(story,t,dr):

    tl = []

    for s in story.sentences:
        for y in s.wbow:
            if s.wbow[y] or y in t:
                tl.append((s,y))

    for n in t:
        i = map(lambda x:x[1],tl).index(n)
        if "B" in dr:
            for d,y in enumerate(reversed(tl[:i]),2):
                y[0].wbow[y[1]] = [(w,wt/log(d,10)) for w,wt in y[0].wbow[y[1]]]
        if "F" in dr:
            for d,y in enumerate(tl[i+1:],2):
                y[0].wbow[y[1]] = [(w,wt/log(d,10)) for w,wt in y[0].wbow[y[1]]]
                
        
def ilpnd(s,t):

    for n in t:
        phr,d,prev = n.parentphrase(),2,[]
        while phr:
            for w in filter(lambda x:x not in prev,phr.parsetree()):
                if w.isword():
                    s.wbow[w] = [(v,(wt / log(d,len(s.words))))
                                 for v,wt in s.wbow[w]]
                elif w.pos == "SBAR":
                    break
            prev = phr.parsetree()
            if phr.pos[:1] == "S":
                break
            elif phr.parents:
                phr = phr.parentphrase() or phr.parents[0]
            else:
                break
            d += 1


def negtokens(s):

    return ({d for g,d,r in s.parse.depgraph() if r == "neg"} |
            {w for w in s.words
             if w.lemma in ["hardly","lack","none","never","nowhere","not"
                            "nothing","nobody","nor","neither","no"]})


def checkanswer(answers, snum, qnum, scores):
    topans = [a for a, s in enumerate(scores) if s == max(scores)]

    if (ord(answers[snum][qnum]) - 0x41) in topans:
        return 1.0 / len(topans)
    else:
        return 0.0

