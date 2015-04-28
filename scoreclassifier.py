import cPickle as pickle
from classes import answers as ans
from collections import OrderedDict
from scorers import checkscores
import sys

import numpy as np
from sklearn.linear_model import LogisticRegression


def load_scores(dataset):
    scores = OrderedDict([
        ("slidingwindow", []),
        ("distance", []),
        ("bowall", []),
        ("rte", []),
        ("selectsent", []),
        ("ngram", []),
    ])
    for score in scores:
        with open("rbs/" + dataset + "." + score, "r") as fl:
            scores[score] = pickle.load(fl)
    return scores


def answer_binary_vector(answers):
    vector = []
    for answer_set in answers:
        for answer in answer_set:
            if answer == "A":
                vector += [1, 0, 0, 0]
            if answer == "B":
                vector += [0, 1, 0, 0]
            if answer == "C":
                vector += [0, 0, 1, 0]
            if answer == "D":
                vector += [0, 0, 0, 1]
    return vector

if __name__ == "__main__":

    if not sys.argv[2:]:
        sys.stderr.write("Usage: python %s <train> <test>\n" % (sys.argv[0]))
        exit()
    else:
        dataset_train = sys.argv[1]
        dataset_test = sys.argv[2]

    answers_train = list(ans(dataset_train))
    answers_test = list(ans(dataset_test))

    scores_train = load_scores(dataset_train).values()
    scores_test = load_scores(dataset_test).values()
    true_train = answer_binary_vector(answers_train)
    true_test = answer_binary_vector(answers_test)

    train_X = np.array(zip(*scores_train))
    test_X = np.array(zip(*scores_test))
    train_y = np.array(true_train)
    test_y = np.array(true_test)

    C = 1e2
    model = LogisticRegression(C=C).fit(train_X, train_y)
    X = model.predict_proba(test_X)

    results = checkscores(answers_test, [x[1] for x in X])

    print results
