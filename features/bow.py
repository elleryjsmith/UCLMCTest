import sys
sys.path.insert(0, '../')
from UCLMCTest.classes import storyparser, Question, answers
from UCLMCTest.grading import grading
from UCLMCTest.vectors import results, YVectorQA, YVectorQ
import nltk
import numpy as np
import cPickle as pickle
import os
from UCLMCTest.selection import filtered_story

STOPWORDS = nltk.corpus.stopwords.words('english')


def bow(s1, s2, bow_filter=None):
    if bow_filter:
        s1 = [t for t in s1 if t[2] == bow_filter]
        s2 = [t for t in s2 if t[2] == bow_filter]

    set1 = {l for w, l, p in s1 if l not in STOPWORDS} \
        | {w for w, l, p in s1 if w not in STOPWORDS}
    set2 = {l for w, l, p in s2 if l not in STOPWORDS} \
        | {w for w, l, p in s2 if w not in STOPWORDS}
    return set1 & set2


def previous_bow(s1, s2):
    sim = []
    for w1, l1, p1 in s1:
        if w1 in STOPWORDS or l1 in STOPWORDS:
            continue
        for w2, l2, p2 in s2:
            if w2 in STOPWORDS or l2 in STOPWORDS:
                continue
            elif l2 == l1:
                sim.append((w1, l1, p1))
                break
    return sim


def score(story, question_n, answer_n, bow_filter=None):
    question = story.questions[question_n]
    answer = question.answers[answer_n]
    qa_pair = question.qsentence.parse.lemma + answer.parse.lemma
    similarities = [bow(qa_pair, s.parse.lemma, bow_filter=bow_filter) for s in story.sentences]
    return (max([len(s) for s in similarities]), similarities)


def scoreAll(story, question_n, answer_n, bow_filter=None):
    question = story.questions[question_n]
    answer = question.answers[answer_n]
    qa_pair = question.qsentence.parse.lemma + answer.parse.lemma
    lemma_story = [l for s in story.sentences for l in s.parse.lemma]
    similarities = bow(qa_pair, lemma_story, bow_filter=bow_filter)
    return (len(similarities), similarities)


def scoreComplement(story, question_n, answer_n, bow_filter=None):
    question = story.questions[question_n]
    answer = question.answers[answer_n]
    qa_pair = question.qsentence.parse.lemma + answer.parse.lemma
    lemma_story = [l for s in story.sentences for l in s.parse.lemma]
    similarities = bow(qa_pair, lemma_story, bow_filter=bow_filter)
    return (len(answer.parse.lemma) - len(similarities), similarities)


def bow_q_select(story, question_n, sentence_n):
    question = story.questions[question_n].qsentence.parse.lemma
    sentence = story.sentences[sentence_n].parse.lemma
    return bow(question, sentence, bow_filter=None)


def bow_qa_select(story, question_n, sentence_n):
    question = story.questions[question_n].qsentence.parse.lemma
    answers = [
        l
        for a in story.questions[question_n].answers
        for l in a.parse.lemma
    ]
    sentence = story.sentences[sentence_n].parse.lemma
    return bow(question + answers, sentence, bow_filter=None)


# This returns [number of bagofwords] or [normalized bagofwords] or [sigmoid bagofwords]
def XVectorQA(stories, norm=None, sigmoid_k=50,
              mode=None, score_f=score, bow_filter=None,
              select_f=None, select_limit=2):
    X = []
    for story in stories:
        for q, question in enumerate(story.questions):
            if mode and question.mode != mode:
                continue

            corpus = story
            if select_f:
                corpus = filtered_story(
                    story, q,
                    limit=select_limit, score_f=select_f
                )

            qa_scores = [score_f(corpus, q, a, bow_filter=bow_filter)[0] for a, _ in enumerate(question.answers)]

            if (norm == "question"):
                qa_scores = np.array(qa_scores)
                qa_scores = (qa_scores / np.linalg.norm(qa_scores)).tolist()
            if (norm == "sigmoid"):
                qa_scores = np.asarray(qa_scores)
                qa_scores = (qa_scores / np.linalg.norm(qa_scores))
                qa_scores = (2 / ((1+ np.exp(-sigmoid_k*(qa_scores-np.mean(qa_scores)))))-1).tolist()

            X = X + qa_scores
    if (norm == "all"):
        X = np.array(X)
        X = (X / np.linalg.norm(X)).tolist()

    return X


# This returns [(score, confidence)]
def XVectorQ(stories, norm=None, sigmoid_k=100, mode=None,
             score_f=score, bow_filter=None, select=None,
             select_f=None, select_limit=2):
    X = []
    for story in stories:
        for q, question in enumerate(story.questions):
            if mode and question.mode != mode:
                continue

            corpus = story
            if select_f:
                corpus = filtered_story(
                    story, q,
                    limit=select_limit, score_f=select_f
                )

            qa_scores = [score_f(corpus, q, a, bow_filter=bow_filter)[0] for a, _ in enumerate(question.answers)]

            if (norm == "question"):
                qa_scores = np.array(qa_scores)
                qa_scores = (qa_scores / np.linalg.norm(qa_scores)).tolist()
            if (norm == "sigmoid"):
                qa_scores = np.array(qa_scores)
                qa_scores = (qa_scores / np.linalg.norm(qa_scores)).tolist()
                qa_scores = (qa_scores / (1+ np.exp(-sigmoid_k*(qa_scores-np.mean(qa_scores))))).tolist()

            answer = qa_scores.index(max(qa_scores))
            X.append((answer, qa_scores[answer]))
    if (norm == "all"):
        X = np.array(X)
        X = (X / np.linalg.norm(X)).tolist()

    return X


def baseline(stories, solutions, mode=None, debug=False):
    scored, total = 0, 0
    for story, solution in zip(stories, solutions):
        for q, question in enumerate(story.questions):
            if mode and question.mode != mode:
                continue
            max_index, max_score = -1, (-1, None)
            for a, _ in enumerate(question.answers):
                current_score = score(story, q, a)
                if current_score[0] > max_score[0]:
                    max_index = a
                    max_score = current_score

            best_answer = chr(max_index + 0x41)
            correct = best_answer == solution[q]
            if correct:
                scored += 1

            total += 1
            if (debug):
                print "Correct:%i\nQuestion matched:\n%s\nWords count: %i\nWords matched:\n%s\n\n" % (correct, question, current_score[0], current_score[1])

    return {
        "total": total,
        "scored": scored,
        "accuracy": (scored * 1.0 / total) * 100
    }


def predict(stories, opts=None):
    return XVectorQA(
        stories,
        norm="question",
        select_f=opts["select_f"] if "select_f" in opts else None,
        select_limit=opts["select_limit"] if "select_limit" in opts else None
    )


def predictAll(stories, opts=None):
    return XVectorQA(
        stories,
        norm="question",
        score_f=scoreAll,
        select_f=opts["select_f"] if "select_f" in opts else None,
        select_limit=opts["select_limit"] if "select_limit" in opts else None
    )


def predictAllNN(stories, opts=None):
    return XVectorQA(
        stories,
        score_f=scoreAll,
        bow_filter="NN",
        select_f=opts["select_f"] if "select_f" in opts else None,
        select_limit=opts["select_limit"] if "select_limit" in opts else None
    )


def predictComplement(stories, opts=None):
    return XVectorQA(
        stories,
        score_f=scoreComplement,
        select_f=opts["select_f"] if "select_f" in opts else None,
        select_limit=opts["select_limit"] if "select_limit" in opts else None
    )


def predictAllVB(stories, opts=None):
    return XVectorQA(
        stories,
        score_f=scoreAll,
        bow_filter="VB",
        select_f=opts["select_f"] if "select_f" in opts else None,
        select_limit=opts["select_limit"] if "select_limit" in opts else None
    )

if __name__ == "__main__":
    if len(sys.argv) == 2:
        testset = sys.argv[1]
        stories = list(storyparser(testset))
        solutions = list(answers(testset))
        mode = None
        X = XVectorQA(stories, norm="question", sigmoid_k=10, mode=mode)
        Y = YVectorQ(stories, solutions, mode)
        results(X, Y, verbose=True)
        grading(X, Y, verbose=True)
        # print baseline(stories, solutions, mode=Question.SINGLE, debug=False)
    else:
        sys.stderr.write("Usage: python %s <dataset> (e.g. mc160.dev)\n" % (sys.argv[0]));
