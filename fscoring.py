from classes import storyparser, answers as ans
from scoring import checkanswer, swdistance, setflg
from filters import Filter
from modifiers import settokens
import filters as fl
import modifiers as md
import sys

        
def fscore160(story, qs, an, bow_filter=None, bow_f=None):

    q = story.questions[qs]
    a = q.answers[an]

    settokens(story)
    setflg(True)
    
    filters = [Filter(None,md.baseline160),
               #Filter(None,md.hypernymy),
               Filter(fl.whyquestion,md.whystory),
               #Filter(fl.complexnegative,md.complexnegate),
               Filter(fl.simplenegative,md.simplenegate),
               Filter(fl.tempquestion,md.tempstory),
               ]
    
    for f in filters:
        f.apply(q,a,story)
                    
    return (swdistance(q,a,story),None)


def fscore500(story, q, a, bow_filter=None, bow_f=None):

    q = story.questions[q]
    a = q.answers[a]

    settokens(story)
    setflg(False)

    filters = [Filter(None,md.baseline500),
               #Filter(None,md.hypernymy),
               Filter(fl.whyquestion,md.whystory),
               #Filter(fl.complexnegative,md.complexnegate),
               Filter(fl.simplenegative,md.simplenegate),
               #Filter(fl.tempquestion,md.tempstory),
               ]

    for f in filters:
        f.apply(q,a,story)
    
    return (swdistance(q,a,story),None)



