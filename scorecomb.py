import cPickle as pickle
from scoring import checkanswer
from classes import answers as ans
from collections import OrderedDict as odict
from scorers import mergescores, checkscores
import sys

scores = odict([("slidingwindow",[]),
                ("distance",[]),
                ("bowall",[]),
                #("bow",[]),
                ("rte",[]),
                ("selectsent",[]),
                ("ngram",[]),
                ])


if __name__ == "__main__":


    if not sys.argv[1:]:
        sys.stderr.write("Usage: python %s <dataset>\n" % (sys.argv[0]))
        exit()
    else:
        dataset = sys.argv[1]

        
    answers = list(ans(dataset))
    
    maxprec,minprec,step = 1.0,0.01,2.0
    passes = 10
    weights = [0.0 for _ in scores]
    
    for score in scores:
        with open("rbs/" + dataset + "." + score,"r") as fl:
            scores[score] = pickle.load(fl)

    curr = checkscores(answers,mergescores(scores,weights))

    for _ in range(passes):

        for i,score in enumerate(scores):

            cprec = maxprec
            # I have no idea what I am doing
            while cprec >= minprec:
        
                while 1:
                    
                    prev = weights[i]  
             
                    weights[i] += cprec
                    newsc = checkscores(answers,mergescores(scores,weights))

                    if newsc > curr:

                        curr = newsc

                    else:

                        weights[i] = prev
                        
                        while 1:

                            prev = weights[i]  

                            weights[i] -= cprec
                            newsc = checkscores(answers,mergescores(scores,weights))
                        
                            if newsc > curr:

                                curr = newsc
                        
                            else:
                            
                                weights[i] = prev
                            
                                break

                    break

                cprec /= step

    print curr,weights,scores.keys()

    with open("rbs/" + dataset.split(".")[0] + ".weights","w") as fl:
        pickle.dump(dict(zip(scores.keys(),weights)),fl)
