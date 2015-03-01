from wordnet import WNToken
from classes import storyparser,answers
from math import log
from nltk.corpus import stopwords
from features.bow import XVectorQA
from vectors import results, YVectorQ
from grading import grading


stories = list(storyparser("mc160.dev"))
answers = list(answers("mc160.dev"))
sw = set(stopwords.words("english"))


def wordpairs(s1, s2):

    return {(w1,w2) for w1 in s1 for w2 in s2 if w1.lemma not in sw and w2.lemma not in sw}


def hypernymy(words, weight):

    s = dict()

    for w in set(words) - sw:

        s[w.lemma] = 1.0

        for y in w.synsets:
            for h,d in y.dfs()[1:]:
                if h.lexname() not in s or s[h.lexname()] > weight(d):
                    s[h.lexname()] = weight(d)

    return s


def hypernymbow(s1, s2, weight):

    h1 = hypernymy(s1,weight)
    h2 = hypernymy(s2,weight)

    return sum([h1[m] for m in (set(h1.keys()) & set(h2.keys()))])


def checkanswer(snum, qnum, scores):

    topans = [a for a,s in enumerate(scores) if s == max(scores)]

    if (ord(answers[snum][qnum]) - 0x41) in topans:
        return 1.0 / len(topans)
    else:
        return 0.0


def answerscores(story, question, matchscore, wnscore):

    ascores = []

    for a in question.answers:

        q = a.words + question.qsentence.words
        scores = []

        for s in story.sentences:
    
            score = 0.0

            for w1,w2 in wordpairs(s.words,q):
            
                if w1.lemma == w2.lemma:
                    score += matchscore
                    continue 
                else:
                    score += wnscore(max([s1.highestcommon(s2)[1] for s1 in w1.synsense() for s2 in w2.synsense()]+[0]))
                                            
            scores.append(score / log(len(s.words) + len(q)))

        ascores.append(max(scores))

    return ascores


def hypbowscore(story, q, a, bow_filter):

    return (max([hypernymbow(s.words,story.questions[q].qsentence.words + story.questions[q].answers[a].words,distweight) for s in story.sentences]),None)

def hyptreescore(story, q, a, bow_filter):

    return (answerscores(story,story.questions[q],match,wnmatch)[a],None)


match = 1.0
wnmatch = lambda x : 1.0 / pow(10,x+1)

distweight = lambda x : 1.0 / pow(10,x)


print "Hypernym BOW:"

X = XVectorQA(stories, norm="question", score_f=hypbowscore,sigmoid_k=10, mode=None)
Y = YVectorQ(stories, answers, None)
results(X, Y, verbose=True)
grading(X, Y, verbose=True)

print "Hypernym Tree Matching:"

X = XVectorQA(stories, norm="question", score_f=hyptreescore,sigmoid_k=10, mode=None)
Y = YVectorQ(stories, answers, None)
results(X, Y, verbose=True)
grading(X, Y, verbose=True)
