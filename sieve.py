from classes import storyparser, answers as ans
from scoring import checkanswer, swdistance, setflg
from filters import Filter
from modifiers import settokens
import filters as fl
import modifiers as md
import sys

        
def scorer(scoref, filters):

    score = 0.0

    for i,story in enumerate(stories):
        for j,q in enumerate(story.questions):
            
            scores = []

            for a in q.answers:

                settokens(story)
                
                for f in filters:
                    f.apply(q,a,story)
                    
                scores.append(scoref(q,a,story))
            
            scr = checkanswer(answers,i,j,scores)

            for f in filters:
                f.addscores(scores,scr)
        
            score += scr
        
    return score / (4.0 * (i+1))



stories = list(storyparser("mc160.test"))
answers = list(ans("mc160.test"))


basefilters = [Filter(None,md.baseline160)]

impfilters = [Filter(None,md.baseline160),
              #Filter(None,md.hypernymy),
              Filter(fl.whyquestion,md.whystory),
              #Filter(fl.complexnegative,md.complexnegate),
              Filter(fl.simplenegative,md.simplenegate),
              Filter(fl.tempquestion,md.tempstory),
              ]
    
bsc = scorer(swdistance,basefilters)
imc = scorer(swdistance,impfilters)

print "### mc160.test: %f%%" % (imc*100.0)

for f in impfilters[1:]:
    print f.compare(basefilters[0])


stories = list(storyparser("mc500.test"))
answers = list(ans("mc500.test"))

setflg(False)

basefilters = [Filter(None,md.baseline500)]

impfilters = [Filter(None,md.baseline500),
              #Filter(None,md.hypernymy),
              Filter(fl.whyquestion,md.whystory),
              #Filter(fl.complexnegative,md.complexnegate),
              Filter(fl.simplenegative,md.simplenegate),
              #Filter(fl.tempquestion,md.tempstory),
              ]
    
bsc = scorer(swdistance,basefilters)
imc = scorer(swdistance,impfilters)

print "### mc500.test: %f%%" % (imc*100.0)

for f in impfilters[1:]:
    print f.compare(basefilters[0])




