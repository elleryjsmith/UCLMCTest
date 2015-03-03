from classes import storyparser, answers as ans
from math import log
from features.bow import XVectorQA
from nltk.corpus import stopwords
from sys import argv, stderr

sw = set(stopwords.words("english"))

match = 1.0
wnmatch = lambda x: 1.0 / pow(10, x + 1)


def wordpairs(s1, s2):
    return {
        (w1, w2)
        for w1 in s1
        for w2 in s2
        if w1.lemma not in sw and w2.lemma not in sw
    }


def hypernymbow(h1, h2):
    return sum([h1[m] for m in (set(h1.keys()) & set(h2.keys()))])


def checkanswer(answers, snum, qnum, scores):
    topans = [a for a, s in enumerate(scores) if s == max(scores)]
    if (ord(answers[snum][qnum]) - 0x41) in topans:
        return 1.0 / len(topans)
    else:
        return 0.0


def treeanswerscore(story, question, ansnum, matchscore, wnscore):
    q = question.answers[ansnum].words + question.qsentence.words
    scores = []

    for s in story.sentences:
        score = 0.0
        for w1, w2 in wordpairs(s.words, q):
            if w1.lemma == w2.lemma or w1.token == w2.token:
                score += matchscore
                continue

            score += wnscore(max([
                s1.highestcommon(s2)[1]
                for s1 in w1.synsense()
                for s2 in w2.synsense()
            ] + [0]))
        scores.append((score / log(len(s.words) + len(q)), s))

    return max(scores)


def hypbowscore(story, q, a, bow_filter):
    qn = story.questions[q]
    qa = dict(qn.qsentence.hypernymy.items() + qn.answers[a].hypernymy.items())

    return max([(hypernymbow(s.hypernymy, qa), s) for s in story.sentences])


def hyptreescore(story, q, a, bow_filter):

    return treeanswerscore(story, story.questions[q], a, match, wnmatch)


def hypbow(stories, opts=None):

    return XVectorQA(
        stories,
        norm="question",
        score_f=hypbowscore,
        select_f=opts["select_f"] if "select_f" in opts else None,
        select_limit=opts["select_limit"] if "select_limit" in opts else None
    )


if __name__ == "__main__":

    if len(argv) > 1:

        for dataset in argv[1:]:

            stories = list(storyparser(dataset))
            answers = list(ans(dataset))
            score = 0.0
            for i, story in enumerate(stories):
                for j, question in enumerate(story.questions):
                    score += checkanswer(
                        answers, i, j,
                        [
                            hypbowscore(story, j, k, None)
                            for k, a in enumerate(question.answers)
                        ]
                    )

            print "%s: %f" % (dataset, score / ((i + 1) * 4))
    else:
        stderr.write("Usage: python %s <datasets> (e.g. mc160.dev)\n" % (argv[0]))
