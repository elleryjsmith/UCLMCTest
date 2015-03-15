# Training set
import numpy as np
import sys
import matplotlib.pyplot as plt
from sklearn import linear_model
from classes import storyparser, answers, Question
from features import bow
from sklearn.metrics import accuracy_score
from vectors import results, YVectorQA, YVectorQ
from grading import grading


# methods = [dict(name="Baseline (BOW)", score=bow.predict, opts=None)]
def train(stories, solutions, opts=None):
    # TODO this should be imported in this way
    # features = [m["score"](stories, opts=m["opts"]) for m in methods]
    # X = [tuple(t,) for t in np.asarray(features).T]

    X = np.array(zip(
        *[feature(stories, opts=opts) for feature in opts["features"]]
    ))
    y = np.array(YVectorQA(stories, solutions))
    C = 1e5

    return linear_model.LogisticRegression(C=C).fit(X, y)


def predict(stories, opts=None):

    X = np.array(zip(
        *[feature(stories, opts=opts) for feature in opts["features"]]
    ))

    # TODO this should be loaded not calculated
    if (not opts):
        opts = {}

    if ("trainsets" not in opts):
        opts["trainsets"] = ["mc160.dev"]

    if ("train_stories" not in opts or "train_solutions" not in opts):
        opts["train_stories"] = list(storyparser(opts["trainsets"]))
        opts["train_solutions"] = list(answers(opts["trainsets"]))

    logreg = train(
        opts["train_stories"],
        opts["train_solutions"],
        opts=opts
    )

    return [x[1] for x in logreg.predict_proba(X)]

if __name__ == "__main__":
    testset = "mc160.dev"
    stories = list(storyparser(testset))
    solutions = list(answers(testset))
    mode = Question.SINGLE

    svm_qa(stories, solutions, mode=mode)
