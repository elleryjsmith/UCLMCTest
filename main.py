import json
import sys
import csv
import math
import glob
import operator as op
import functools as ft
import cPickle as pickle

WINMULT = 3
SLEN = 10
CRFIDF = 0

def ans(dataset):

    def corr(x):
        return map(ft.partial(op.eq,ord(x) - 0x41),range(4))

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

    return [{alt:{"word":c["word"],
                  "idf":(t["origidf"] if CRFIDF else c["idf"])},
             "matches":{
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

def score(stories, scoref, word="token",
          coref=False, stopwords=True, negation=False):

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
            
            if negation and story["negativeqs"][i]:
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

def scoredevtrain(stories, answers, settype):

    rtescores = [0.0 for _ in range(len(stories) * 16)]

    setargs("word","token")
    basic = scoreset(stories, answers, rtescores, settype)

    setargs("negation",True)
    negate = scoreset(stories, answers, rtescores, settype)
    setargs("negation",False)

    resetscorefs()
    stems = scoreset(stories, answers, rtescores, settype)

    setargs("coref",True)
    coref = scoreset(stories, answers, rtescores, settype)
    setargs("coref",False)

    setargs("negation",True)
    total = scoreset(stories, answers, rtescores, settype)
    setargs("negation",False)

    resetscorefs()

    return dict(baseline=basic,
                lemmatization=stems,
                negation=negate,
                coreference=coref,
                combined=total)

def windowscores(stories, answers, settype):

    global WINMULT

    rtescores = [0.0 for _ in range(len(stories) * 16)]

    oldwm = WINMULT
    winscores = dict(coref=dict(),nocoref=dict())

    for i in range(1,5):

        WINMULT = i

        setargs("negation",True)
        winscores["nocoref"][i] = scoreset(stories,answers,rtescores,settype)

        setargs("coref",True)
        winscores["coref"][i] = scoreset(stories,answers,rtescores,settype)

        resetscorefs()


    WINMULT = oldwm

    return winscores

def testscores(stories, answers, rtescores, settype):

    sc = dict()

    setargs("negation",True)
    sc["rte"] = scoreset(stories, answers, rtescores, settype)    

    rtescores = [0.0 for _ in range(len(stories) * 16)]
    sc["norte"] = scoreset(stories, answers, rtescores, settype)    

    resetscorefs()

    return sc

def resetscorefs():

    for scoref in scorefs:
        scorefs[scoref]["args"]["coref"] = False
        scorefs[scoref]["args"]["negation"] = False
        scorefs[scoref]["args"]["word"] = "token"

    scorefs[impslidingwindow]["args"]["word"] = "lemma"

def setargs(a, v):

    for scoref in scorefs:
        scorefs[scoref]["args"][a] = v

def scoreset(stories, answers, rtescores, settype, result=True):

    allscores = []

    for scoref in scorefs:

        if scoref != rte:
            scores = score(stories,scoref,**scorefs[scoref]["args"])
        else:
            scores = rtescores
            
        allscores.append([s * scorefs[scoref][settype + "weight"]
                          for s in scores])
 
    return grade(map(sum,zip(*allscores)),answers,result)

def loadstories(dataset):

    with open("datasets/" + dataset + ".json","r") as fl:
        return json.load(fl)

def loadrte(dataset):    

    with open("datasets/" + dataset + ".rte","r") as fl:
        return pickle.load(fl)

def loadcategories(dataset):

    fls = glob.glob("categories/*.txt")

    cts = dict()

    for f in fls:
        with open(f,"r") as fl:
            nm = f.split("/")[1].split(".")[0].replace("|","/")
            cts[nm] = []
            for ln in fl:
                ps = ln.replace("\n","").split(".")[2].split(",")
                cts[nm].append((int(ps[0]) * 4) + int(ps[1]))

    return cts

def devtrainresults():

    print "#Dev+Train Results"
    print "| Description | MC160 | MC500 |\n|---|---|---|"

    data = datasets["devtrain"]["mc160"]
    scores160 = scoredevtrain(data["stories"],data["answers"],data["settype"])
    data = datasets["devtrain"]["mc500"]
    scores500 = scoredevtrain(data["stories"],data["answers"],data["settype"])

    frm = dict()
    for s in scores160:
        if s != "baseline":
            frm[s] = (scores160[s] * 100,
                      (scores160[s] - scores160["baseline"]) * 100,
                      scores500[s] * 100,
                      (scores500[s] - scores500["baseline"]) * 100)

    print "| ImpSW+D | %.2f | %.2f |" % (scores160["baseline"] * 100,
                                       scores500["baseline"] * 100)
    print "| +Negation | %.2f (%.2f) | %.2f (%.2f) |" % frm["negation"]
    print "| +Stemming | %.2f (%.2f) | %.2f (%.2f) |" % frm["lemmatization"]
    print "| +Coreference | %.2f (%.2f) | %.2f (%.2f) |" % frm["coreference"]
    print "| +Combined | %.2f (%.2f) | %.2f (%.2f) |" % frm["combined"]

def windowsizeresults():

    print "#Effect of Window Size"
    print "| Window Size | MC160 | MC160 w/ Coref | MC500 | MC500 w/ Coref |"
    print "|---|---|---|---|---|"

    data = datasets["devtrain"]["mc160"]
    scores160 = windowscores(data["stories"],data["answers"],data["settype"])
    data = datasets["devtrain"]["mc500"]
    scores500 = windowscores(data["stories"],data["answers"],data["settype"])
    
    for i in range(1,5):

        winrow = (i,scores160["nocoref"][i] * 100,scores160["coref"][i] * 100,
                  scores500["nocoref"][i] * 100,scores500["coref"][i] * 100)

        print "| %d sentences | %.2f | %.2f | %.2f | %.2f |" % winrow

def singlemultiresults():

    print "#Single/Multi Split"
    print "| Type | MC160 | MC160 w/ Coref | MC500 | MC500 w/ Coref |"
    print "|---|---|---|---|---|"

    data = datasets["devtrain"]["mc160"]
    multi160 = [i for story in data["stories"] for i in story["multiqs"]]
    rtescores = [0.0 for _ in range(len(data["stories"]) * 16)]
    scores160 = scoreset(data["stories"],data["answers"],rtescores,
                         data["settype"],result=False)
    
    data = datasets["devtrain"]["mc500"]
    multi500 = [i for story in data["stories"] for i in story["multiqs"]]
    rtescores = [0.0 for _ in range(len(data["stories"]) * 16)]
    scores500 = scoreset(data["stories"],data["answers"],rtescores,
                         data["settype"],result=False)

    setargs("coref",True)
    
    data = datasets["devtrain"]["mc160"]
    rtescores = [0.0 for _ in range(len(data["stories"]) * 16)]
    cscores160 = scoreset(data["stories"],data["answers"],rtescores,
                         data["settype"],result=False)
    
    data = datasets["devtrain"]["mc500"]
    rtescores = [0.0 for _ in range(len(data["stories"]) * 16)]
    cscores500 = scoreset(data["stories"],data["answers"],rtescores,
                         data["settype"],result=False)

    resetscorefs()

    ssc160 = [s for i,s in enumerate(scores160) if not multi160[i]]
    ssc160 = sum(ssc160) / len(ssc160)
    msc160 = [s for i,s in enumerate(scores160) if multi160[i]] 
    msc160 = sum(msc160) / len(msc160)
    scsc160 = [s for i,s in enumerate(cscores160) if not multi160[i]]
    scsc160 = sum(scsc160) / len(scsc160)
    mcsc160 = [s for i,s in enumerate(cscores160) if multi160[i]] 
    mcsc160 = sum(mcsc160) / len(mcsc160)

    ssc500 = [s for i,s in enumerate(scores500) if not multi500[i]] 
    ssc500 = sum(ssc500) / len(ssc500)
    msc500 = [s for i,s in enumerate(scores500) if multi500[i]] 
    msc500 = sum(msc500) / len(msc500)
    scsc500 = [s for i,s in enumerate(cscores500) if not multi500[i]]
    scsc500 = sum(scsc500) / len(scsc500)
    mcsc500 = [s for i,s in enumerate(cscores500) if multi500[i]] 
    mcsc500 = sum(mcsc500) / len(mcsc500)

    print "| Single | %.2f | %.2f | %.2f | %.2f |" % (ssc160*100,scsc160*100,
                                                      ssc500*100,scsc500*100)

    print "| Multi | %.2f | %.2f | %.2f | %.2f |" % (msc160*100,mcsc160*100,
                                                     msc500*100,mcsc500*100)

def corefidfresults():

    global CRFIDF

    print "#Coreference IDF Effects"
    print "| Description | MC160 | MC500 |\n|---|---|---|"
    
    setargs("coref",True)

    data = datasets["devtrain"]["mc160"]
    rtescores = [0.0 for _ in range(len(data["stories"]) * 16)]
    ascores160 = scoreset(data["stories"],data["answers"],rtescores,
                         data["settype"],result=True) * 100
    
    data = datasets["devtrain"]["mc500"]
    rtescores = [0.0 for _ in range(len(data["stories"]) * 16)]
    ascores500 = scoreset(data["stories"],data["answers"],rtescores,
                         data["settype"],result=True) * 100

    CRFIDF = 1

    data = datasets["devtrain"]["mc160"]
    rtescores = [0.0 for _ in range(len(data["stories"]) * 16)]
    bscores160 = scoreset(data["stories"],data["answers"],rtescores,
                         data["settype"],result=True) * 100
    
    data = datasets["devtrain"]["mc500"]
    rtescores = [0.0 for _ in range(len(data["stories"]) * 16)]
    bscores500 = scoreset(data["stories"],data["answers"],rtescores,
                         data["settype"],result=True) * 100

    resetscorefs()    
    CRFIDF = 0

    print "| Using Original IDF | %.2f | %.2f |" % (bscores160,bscores500)
    print "| Calculating IDF After Coreference | %.2f | %.2f |" % (ascores160,
                                                                   ascores500)

def categoryresults():

    print "#Results by Category"
    print ("| Category | MC160 % of Questions | MC160 Score | MC160 w/ Coref "
           "| MC500 % of Questions | MC500 Score | MC500 w/ Coref |")
    print "|---|---|---|---|---|---|---|"

    tmpstories = loadstories("mc500.train")
    tmpans = ans("mc500.train")
    tmptype = "mc500"
    tmprte = [0.0 for _ in range(len(tmpstories) * 16)]

    scores = scoreset(tmpstories,tmpans,tmprte,tmptype,result=False)
    overall = sum(scores) * 100.0 / len(scores)

    setargs("coref",True)
    corefscores = scoreset(tmpstories,tmpans,tmprte,tmptype,result=False)
    corefoverall = sum(corefscores) * 100.0 / len(corefscores)

    resetscorefs()

    for category in categories:

        filtered = [s for i,s in enumerate(scores)
                    if i in categories[category]]
        coreffiltered = [s for i,s in enumerate(corefscores)
                         if i in categories[category]]

        fsc = sum(filtered) * 100.0 / len(filtered)
        fscd = fsc - overall
        cfc = sum(coreffiltered) * 100.0 / len(coreffiltered)
        cfcd = cfc - overall
        num = len(categories[category]) * 100.0 / (len(tmpstories) * 4)

        print ("| %s | - | - | - | %.2f | %.2f (%.2f) | %.2f (%.2f) |"
               % (category,num,fsc,fscd,cfc,cfcd))

def testresults():

    print "#Test Results"
    print "| Description | MC160 | MC500 |\n|---|---|---|"    


    data = datasets["test"]["mc160"]
    scores160 = testscores(data["stories"],data["answers"],
                           data["rtescores"],data["settype"])
    data = datasets["test"]["mc500"]
    scores500 = testscores(data["stories"],data["answers"],
                           data["rtescores"],data["settype"])

    print "| Without RTE | %.2f | %.2f |" % (scores160["norte"] * 100,
                                             scores500["norte"] * 100)

    print "| With RTE | %.2f (%.2f) | %.2f (%.2f) |" % (scores160["rte"] * 100,
                                                        (scores160["rte"] -
                                                         scores160["norte"])
                                                        * 100,
                                                        scores500["rte"] * 100,
                                                        (scores500["rte"] -
                                                         scores500["norte"])
                                                        * 100)
    

scorefs = {distance:{"mc160weight":10,
                     "mc500weight":11,
                     "args":dict(word="token",
                                 coref=False,
                                 stopwords=False,
                                 negation=False)
                     },
           
           impslidingwindow:{"mc160weight":1,
                             "mc500weight":1,
                             "args":dict(word="lemma",
                                         coref=False,
                                         stopwords=True,
                                         negation=False)
                             },
           
           bowall:{"mc160weight":1,
                   "mc500weight":6,
                   "args":dict(word="token",
                               coref=False,
                               stopwords=False,
                               negation=False)
                   },
           
           rte:{"mc160weight":40,
                "mc500weight":25,
                "args":dict()
                },
           
           }

datasets = {"devtrain":{"mc160":{"stories":(loadstories("mc160.dev") +
                                            loadstories("mc160.train")),
                                 "answers":(ans("mc160.dev") +
                                            ans("mc160.train")),
                                 "rtescores":(loadrte("mc160.dev") +
                                              loadrte("mc160.train")),
                                 "settype":"mc160",
                                 },
                        "mc500":{"stories":(loadstories("mc500.dev") +
                                            loadstories("mc500.train")),
                                 "answers":(ans("mc500.dev") +
                                            ans("mc500.train")),
                                 "rtescores":(loadrte("mc500.dev") +
                                              loadrte("mc500.train")),
                                 "settype":"mc500",
                                 },
                        },
            "test":{"mc160":{"stories":loadstories("mc160.test"),
                             "answers":ans("mc160.test"),
                             "rtescores":loadrte("mc160.test"),
                             "settype":"mc160",
                             },
                    "mc500":{"stories":loadstories("mc500.test"),
                             "answers":ans("mc500.test"),
                             "rtescores":loadrte("mc500.test"),
                             "settype":"mc500",
                             },
                    },
            }


categories = loadcategories("mc500.train")


if __name__ == "__main__":

    devtrainresults()
    windowsizeresults()
    singlemultiresults()
    corefidfresults()
    categoryresults()
    testresults()

