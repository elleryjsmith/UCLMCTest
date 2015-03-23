from classes import storyparser, answers as ans
from math import log
from scoring import checkanswer
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
    return sum([h1[m] for m in (set(h1.keys()) & set(h2))])


def hypernymbow_list(h1, h2):
    return [h1[m] for m in (set(h1.keys()) & set(h2))]


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


def hypbowscore(story, q, a, bow_filter=None, bow_f=None):
    qn = story.questions[q]
    qa = qn.qsentence.coreference + qn.answers[a].coreference

    return max([(hypernymbow(s.hypernymy, qa), s) for s in story.sentences])


def hyptreescore(story, q, a, bow_filter=None, bow_f=None):

    return treeanswerscore(story, story.questions[q], a, match, wnmatch)


def hyp_q_select(story, question_n, sentence_n):
    question = story.questions[question_n].qsentence.hypernymy
    sentence = story.sentences[sentence_n].hypernymy
    return hypernymbow(question, sentence)


def hyp_qa_select(story, question_n, sentence_n):
    question = story.questions[question_n].qsentence.coreference
    answers = [
        l
        for a in story.questions[question_n].answers
        for l in a.coreference
    ]
    sentence = story.sentences[sentence_n].hypernymy
    return hypernymbow(sentence,question + answers)


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
            score,answered = 0.0,0
            for i, story in enumerate(stories):
                for j, question in enumerate(story.questions):
                    if 1 or question.mode:
                        score += checkanswer(
                            answers, i, j,
                            [
                                hypbowscore(story, j, k, None)
                                for k, a in enumerate(question.answers)
                                ]
                            )
                        answered += 1

            print "%s: %f" % (dataset, score * 1.0 / answered)
    else:
        stderr.write("Usage: python %s <datasets> (e.g. mc160.dev)\n" % (argv[0]))
