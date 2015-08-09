import operator as op
from stories import datasets
from scoring import scoredataset

def printresults():

    scores = {d:{"verbose":scoredataset(d,verbose=True),
                 "normal":scoredataset(d)}
              for d in ["dev","train","devtrain","test"]}
    

    print "Main Results\n========"
    print "#Dev+Train Results"
    printverbose("devtrain",scores["devtrain"]["verbose"]["norte"],heading=False)
    print "#Test Results"
    printrte("test",scores["test"]["normal"]["norte"]["best"],
             scores["test"]["normal"]["rte"]["best"],heading=False)

    printall("Detailed Results",printverbose,scores,"verbose")
    
    printall("Single/Multi Split",printsinglemulti,scores,"normal")

    printall("Results by Category",printcategories,scores,"normal")

def printall(name, fn, scores, vnorm):

    print "%s\n=======" % (name)
    for d in scores:
        if d != "test": fn(d,scores[d][vnorm]["norte"])
    testrte(fn,scores["test"][vnorm])

def testrte(fn, scores):

    print "#test (no rte)"; fn("test",scores["norte"],heading=False)
    print "#test (rte)"; fn("test",scores["rte"],heading=False)

def generatescores():

    scores = {d:scoredataset(d,grade=False) for d in ["dev","train","test"]}

    for d in scores:
        for s in ["160","500"]:
            for r in ["rte","norte"]:
                with open("scores/mc" + s + "." + d + "_" + r + ".scores","w") as fl:
                    writescores(scores[d][r]["best"][s],fl)
            

def writescores(scores, fl):

    for i,s in enumerate(scores):
        if i % 4 != 3:
            fl.write("%f," % (s))
        if i % 4 == 3:
            fl.write("%f\t" % (s))
        if i % 16 == 15:
            fl.write("\n")
            
def average(l):

    return sum(l,0.0) * 100 / len(l)

def diff(l1, l2):

    return average(l2) - average(l1)

def printverbose(name, scores, heading=True):

    if heading: print "#%s" % (name)
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

def multiqs(stories):

    return [i for story in stories for i in story["multiqs"]]

def filterqs(scores, mqs, multi=True):

    return average([s for s,f in zip(scores,mqs) if f == multi])

def printsinglemulti(name, scores, heading=True):

    if heading: print "#%s" % (name)
    print "| Type | MC160 | MC500 | MC160 (No Rules) | MC500 (No Rules) |"
    print "|---|---|---|---|---|"

    stories160,stories500 = datasets[name]["160"]["stories"],datasets[name]["500"]["stories"]
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

def printcategories(name, scores, heading=True):

    if heading: print "#%s" % (name)
    print ("| Category | MC160 % of Questions | MC160 (With Rules) "
           "| MC160 (No Rules) | MC160 (Coref on All) "
           "| MC500 % of Questions | MC500 (With Rules) "
           "| MC500 (No Rules) | MC500 (Coref on All) |")
    print "|---|---|---|---|---|---|---|---|---|"

    row = ("| %s | %.2f (%d) | %.2f (%+.2f) | %.2f (%+.2f) | %.2f (%+.2f) |"
           " %.2f (%d) | %.2f (%+.2f) | %.2f (%+.2f) | %.2f (%+.2f) |")

    stories160,stories500 = datasets[name]["160"]["stories"],datasets[name]["500"]["stories"]
    cats = {"160":categorise(stories160),"500":categorise(stories500)}

    sc = {d:{n.replace("|","/"):catprop(stories160 if d == "160" else stories500,c)
             + filtercat(c,scores["best"][d],scores["best"][d])
             + filtercat(c,scores["norules"][d],scores["best"][d])
             + filtercat(c,scores["coref"][d],scores["best"][d])
             for n,c in cats[d].items()} for d in sorted(cats)}
                                           
    for c in sc["500"]:
        if c in sc["160"]:
            print row % ((c,) + sc["160"][c] + sc["500"][c])
        else:
            print ("| %s | - | - | - | - | %.2f (%d) | %.2f (%+.2f) | %.2f (%+.2f) | %.2f (%+.2f) |"
                   % ((c,) + sc["500"][c]))
    for c in sc["160"]:
        if c not in sc["500"]:
            print ("| %s | %.2f (%d) | %.2f (%+.2f) | %.2f (%+.2f) | %.2f (%+.2f) | - | - | - | - |"
                   % ((c,) + sc["160"][c]))

def printrte(name, norte, rte, heading=True):

    if heading: print "#%s" % (name)
    print "| Description | MC160 | MC500 |"
    print "|---|---|---|"    
    print ("| Without RTE | %.2f | %.2f |"
           % (average(norte["160"]),average(norte["500"])))
    print ("| With RTE | %.2f (%+.2f) | %.2f (%+.2f) |"
           % (average(rte["160"]),diff(norte["160"],rte["160"]),
              average(rte["500"]),diff(norte["500"],rte["500"])))
