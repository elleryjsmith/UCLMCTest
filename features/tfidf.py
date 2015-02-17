import sys
sys.path.insert(0, '../')
from UCLMCTest.classes import storyparser, Question, answers
from UCLMCTest.grading import grading
from UCLMCTest.vectors import results, YVectorQA, YVectorQ
import nltk
import numpy as np
import bow
from sklearn.feature_extraction.text import TfidfVectorizer


def tfidf(story):
    vectorizer = TfidfVectorizer(min_df=1)
    lemma_story = [" ".join([l[1] for l in s.parse.lemma if l[1] != None]) for s in story.sentences]
    vectorizer.fit_transform(lemma_story) # although this must be fixed
    idf = vectorizer.idf_
    return dict(zip(vectorizer.get_feature_names(), idf))


def cooccurrence(story, question_n, answer_n):
    question = story.questions[question_n]
    answer = question.answers[answer_n]
    qa_pair = answer.parse.lemma
    lemma_story = [l for s in story.sentences for l in s.parse.lemma]
    return bow.bow(qa_pair, lemma_story)


# This returns [(score, confidence)]
def XVectorQA(stories, mode=None):
    X = []
    for story in stories:
        idfs = tfidf(story)
        # print idfs
        for q, question in enumerate(story.questions):
            if mode and question.mode != mode:
                continue
            qa_pairs = [cooccurrence(story, q, a) for a, _ in enumerate(question.answers)]
            idf_weights = [idfs[w.lower()] for qa_pair in qa_pairs for w in qa_pair if w in idfs]
            X.append(idf_weights and np.mean(idf_weights) or 0)
    return X


def predict(stories, opts=None):
    return XVectorQA(stories)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        testset = sys.argv[1]
        stories = list(storyparser(testset))
        solutions = list(answers(testset))
        mode = None
        X = XVectorQA(stories, mode=mode)
        Y = YVectorQ(stories, solutions, mode)
        # results(X, Y, verbose=True)
        grades = grading(X, Y, verbose=True)
        print sum(grades) / len(grades)
        # print baseline(stories, solutions, mode=Question.SINGLE, debug=False)
    else:
        sys.stderr.write("Usage: python %s <dataset> (e.g. mc160.dev)\n" % (sys.argv[0]));
