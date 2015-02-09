import sys
sys.path.insert(0, '../')
from gensim.models import Word2Vec
from nltk.corpus import brown
from UCLMCTest.classes import storyparser, Question, answers
from UCLMCTest.grading import grading
from UCLMCTest.vectors import results, YVectorQA, YVectorQ
import numpy as np

model = Word2Vec(brown.sents())

def score(story, question_n, answer_n):
    question = story.questions[question_n]
    answer = question.answers[answer_n]
    qa_pair = question.qsentence.parse.lemma + answer.parse.lemma
    similarities = [model.n_similarity([x[0] for x in qa_pair if "ROOT" != x[0]], [x[0] for x in s.parse.lemma]) for s in story.sentences]
    return (max([len(s) for s in similarities]), similarities)


# This returns [number of bagofwords] or [normalized bagofwords] or [sigmoid bagofwords]
def XVectorQA(stories, norm=None, mode=None):
    X = []
    for story in stories:
        for q, question in enumerate(story.questions):
            if mode and question.mode != mode:
                continue
            qa_scores = [score(story, q, a)[0] for a, _ in enumerate(question.answers)]
            if (norm == "question"):
                qa_scores = np.array(qa_scores)
                qa_scores = (qa_scores / np.linalg.norm(qa_scores)).tolist()
            X = X + qa_scores

    return X


# This returns [(score, confidence)]
def XVectorQ(stories, norm=None, sigmoid_k=100, mode=None):
    X = []
    for story in stories:
        for q, question in enumerate(story.questions):
            if mode and question.mode != mode:
                continue
            qa_scores = [score(story, q, a)[0] for a, _ in enumerate(question.answers)]

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
    return XVectorQA(stories, norm="question")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        testset = sys.argv[1]
        stories = list(storyparser(testset))
        solutions = list(answers(testset))
        mode = None
        X = XVectorQA(stories, mode=mode)
        Y = YVectorQ(stories, solutions, mode)
        results(X, Y, verbose=True)
        grading(X, Y, verbose=True)
        # print baseline(stories, solutions, mode=Question.SINGLE, debug=False)
    else:
        sys.stderr.write("Usage: python %s <dataset> (e.g. mc160.dev)\n" % (sys.argv[0]));
