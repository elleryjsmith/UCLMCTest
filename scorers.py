from scoring import checkanswer
from modifiers import settokens
from filters import simplenegative

def mergescores(scores, weights):
    
    return [sum(z) for z in zip(*[[s * weights[i] for s in scores[sc]]
                                  for i,sc in enumerate(scores)])]

def perms(l, s):

    for i in xrange(len(l) ** s):

        p = []

        for j in xrange(s):
            p.append(l[(i / (len(l) ** j)) % len(l)])

        yield p

def scorer(stories, answers, scoref, filters):

    score = 0.0

    for i,story in enumerate(stories):

        settokens(story)
        
        for f in filters:
            f(None,None,story)

        for j,q in enumerate(story.questions):

            if simplenegative(q,None,story):
                score += checkanswer(answers,i,j,
                                     [-scoref(q,a,story) for a in q.answers])
            else:
                score += checkanswer(answers,i,j,
                                     [scoref(q,a,story) for a in q.answers])

    return score / (4.0 * (i+1))

def getscores(stories, scoref, filters):

    score = []

    for story in stories:

        settokens(story)
        
        for f in filters:
            f(None,None,story)
            
        for q in story.questions:
            if simplenegative(q,None,story):
                score.extend([-scoref(q,a,story) for a in q.answers])
            else:
                score.extend([scoref(q,a,story) for a in q.answers])

    return score


def checkscores(answers, s):
    
    score = 0.0

    for i in range(0,len(s),4):
        score += checkanswer(answers,
                             (i + 1) / 16,
                             ((i + 1) / 4) % 4,
                             s[i:i+4])

    return score / (len(s) / 4.0)

