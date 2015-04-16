from classes import storyparser, answers as ans
from filters import Filter
from modifiers import settokens
from scoring import checkanswer
from scorers import checkscores, getscores, scorer
import filters as fl
import modifiers as md
import scoring as sc
import sys
import cPickle as pickle
import numpy as np


filters = [md.tokenize,
           md.lemmatize,
           md.coreference,
           md.stopwords,
           md.hypernymy,
           md.tokenfrequency,
           ]

def distance(x,y,z):
    return -sc.distance(x,y,z)

scorefns = [sc.slidingwindow,
            sc.bow,
            sc.bowall,
            sc.selectsent,
            sc.ngram,
            distance,
            ]

if __name__ == "__main__":

    if not sys.argv[1:]:
        sys.stderr.write("Usage: python %s <dataset>\n" % (sys.argv[0]))
        exit()
    else:
        dataset = sys.argv[1]


    stories = list(storyparser(dataset))
    answers = list(ans(dataset))


    try:
        with open("rbs/" + dataset.split(".")[0] + ".optimal","r") as fl:
            optimal = pickle.load(fl)
    except FileNotFoundError:
        optimal = {}

    for scorefn in scorefns:
    
        cfl = filters

        scrx = getscores(stories,scorefn,cfl)
        curr = checkscores(answers,scrx)

        while cfl:

            prev = cfl
            
            for f in cfl[:]:

                nfl = [fl for fl in cfl if fl != f]
                nscrx = getscores(stories,scorefn,nfl)
                nsc = checkscores(answers,nscrx)

                if nsc > curr:
                    curr = nsc
                    cfl = nfl
                    scrx = nscrx
                    break
            else:
                break
                
        print curr,cfl,scorefn

        optimal[scorefn.__name__] = [f.__name__ for f in cfl]
    
        with open("rbs/" + dataset + "." + scorefn.__name__,"w") as fl:
            pickle.dump(scrx,fl)
        
    with open("rbs/" + dataset.split(".")[0] + ".optimal","w") as op:
        pickle.dump(optimal,op)
