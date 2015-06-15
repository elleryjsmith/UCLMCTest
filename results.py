import operator as op
from stories import datasets
from scoring import scoredevtrain, windowscores, testscores

def printresults():

    devtrain = scoredevtrain(verbose=True)
    bestcoref = scoredevtrain(verbose=False)
    test = testscores()
    window = windowscores()
    
    printdevtrain(devtrain)
    printwindowsize(window)
    printtest(test)
    printsinglemulti(datasets["devtrain"]["160"]["stories"],
                     datasets["devtrain"]["500"]["stories"],bestcoref)
    printcategories(datasets["devtrain"]["160"]["stories"],
                    datasets["devtrain"]["500"]["stories"],bestcoref)

def average(l):

    return sum(l,0.0) * 100 / len(l)

def diff(l1, l2):

    return average(l2) - average(l1)

def printdevtrain(scores):

    print "#Dev+Train Results"
    print "| Description | MC160 | MC500 |\n|---|---|---|"

    row = "| %s | %.2f (%+.2f) | %.2f (%+.2f) |"
    
    names = {"1neg":"+Negation",
             "2stem":"+Stemming",
             "3coref":"+Coreference",
             "4best":"+Combined"}

    print "| ImpSW+D | %.2f | %.2f |" % (average(scores["base"]["160"]),
                                         average(scores["base"]["500"]))
    
    for n,r in sorted(scores.items()):
        if n != "base":
            print row % (names[n],
                         average(r["160"]),diff(scores["base"]["160"],r["160"]),
                         average(r["500"]),diff(scores["base"]["500"],r["500"]))

def printwindowsize(scores):

    print "#Effect of Window Size"
    print "| Window Size | MC160 | MC160 (No Rules) | MC500 | MC500 (No Rules) |"
    print "|---|---|---|---|---|"

    row = "| %d sentences | %.2f | %.2f | %.2f | %.2f |"
    
    for winlen,sc in scores.items():
        print row % (winlen,
                     average(sc["best"]["160"]),average(sc["norules"]["160"]),
                     average(sc["best"]["500"]),average(sc["norules"]["500"]))

def multiqs(stories):

    return [i for story in stories for i in story["multiqs"]]

def filterqs(scores, mqs, multi=True):

    return average([s for s,f in zip(scores,mqs) if f == multi])

def printsinglemulti(stories160, stories500, scores):

    print "#Single/Multi Split"
    print "| Type | MC160 | MC500 | MC160 (No Rules) | MC500 (No Rules) |"
    print "|---|---|---|---|---|"
    
    sc = [(scores[sc][t],multiqs(stories160 if t == "160" else stories500))
          for sc in sorted(scores) for t in scores[sc] if sc != "coref"]

    print ("| Single | %.2f | %.2f | %.2f | %.2f |"
           % tuple([filterqs(s,m,multi=False) for s,m in sc]))
    print ("| Multi | %.2f | %.2f | %.2f | %.2f |"
           % tuple([filterqs(s,m) for s,m in sc]))

def categorise(stories):

    cats = dict()

    for i,story in enumerate(stories):
        for j,q in enumerate(story["categories"]):
            for c in q:
                if c not in cats:
                    cats[c] = [(i * 4) + j]
                else:
                    cats[c].append((i * 4) + j)

    return cats

def filtercat(cat, scores, overall):

    fsc = [sc for i,sc in enumerate(scores) if i in cat]

    return (average(fsc),diff(overall,fsc))

def catprop(stories, cat):

    return (len(cat) * 25.0 / len(stories),len(cat))

def printcategories(stories160, stories500, scores):

    print "#Results by Category"
    print ("| Category | MC160 % of Questions | MC160 (With Rules) "
           "| MC160 (No Rules) | MC160 (Coref on All) "
           "| MC500 % of Questions | MC500 (With Rules) "
           "| MC500 (No Rules) | MC500 (Coref on All) |")
    print "|---|---|---|---|---|---|---|"

    row = ("| %s | %.2f (%d) | %.2f (%+.2f) | %.2f (%+.2f) | %.2f (%+.2f) |"
           " %.2f (%d) | %.2f (%+.2f) | %.2f (%+.2f) | %.2f (%+.2f) |")

    cats = {"160":categorise(stories160),"500":categorise(stories500)}

    sc = {d:{n.replace("|","/"):catprop(stories160 if d == "160" else stories500,c)
             + filtercat(c,scores["best"][d],scores["best"][d])
             + filtercat(c,scores["norules"][d],scores["best"][d])
             + filtercat(c,scores["coref"][d],scores["best"][d])
             for n,c in cats[d].items()} for d in sorted(cats)}
    
    for c in sc["160"]:
        print row % ((c,) + sc["160"][c] + sc["500"][c])

def printtest(scores):

    print "#Test Results"
    print "| Description | MC160 | MC160 (With Rules) | MC500 | MC500 (With Rules)"
    print "|---|---|---|"    
    print ("| Without RTE | %.2f | %.2f | %.2f | %.2f |"
           % (average(scores["norte"]["norules"]["160"]),
              average(scores["norte"]["rules"]["160"]),
              average(scores["norte"]["norules"]["500"]),
              average(scores["norte"]["rules"]["500"])))
    print ("| With RTE | %.2f (%+.2f) | %.2f (%+.2f) | %.2f (%+.2f) | %.2f (%+.2f)"
           % (average(scores["rte"]["norules"]["160"]),
              diff(scores["norte"]["norules"]["160"],
                   scores["rte"]["norules"]["160"]),
              average(scores["rte"]["rules"]["160"]),
              diff(scores["norte"]["rules"]["160"],
                   scores["rte"]["rules"]["160"]),
              average(scores["rte"]["norules"]["500"]),
              diff(scores["norte"]["norules"]["500"],
                   scores["rte"]["norules"]["500"]),
              average(scores["rte"]["rules"]["500"]),
              diff(scores["norte"]["rules"]["500"],
                   scores["rte"]["rules"]["500"])))
