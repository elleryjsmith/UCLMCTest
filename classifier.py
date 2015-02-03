# Training set
import numpy as np
import sys
import matplotlib.pyplot as plt
from sklearn import svm
from classifiers.perceptron import Perceptron
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
        bow.predict(stories),
    ))
    y = np.array(YVectorQA(stories, solutions))
    C = 4.0

    return svm.SVC(kernel='linear', C=C, probability=True).fit(X, y)


def predict(stories, opts=None):

    X = np.array(zip(
        bow.predict(stories),
    ))

    # TODO this should be loaded not calculated
    trainset = "mc160.train"
    train_stories = list(storyparser(trainset))
    train_solutions = list(answers(trainset))
    svc = train(train_stories, train_solutions, opts=opts)
    # END

    return [x[1] for x in svc.predict_proba(X)]


def svm_qa(stories, solutions, mode=None):
    qa = bow.XVectorQA(stories, norm="sigmoid", sigmoid_k=10, mode=mode)
    X = np.array(zip(
        qa,
        [0] * len(qa)
    ))
    y = np.array(YVectorQA(stories, solutions, mode=mode))
    h=0.01
    C=1.0

    svc = svm.SVC(kernel='linear', C=C).fit(X, y)
    print "Single QA Prediction " + str(svc.predict(X))
    print "Single QA Actual     " + str(y)
    print "Single QA Accuracy   " + str(svc.score(X, y) * 100) + "%"
    print "Single QA Correct   " + str(accuracy_score(y, svc.predict(X), normalize=False))

    results(svc.predict(X), YVectorQ(stories, solutions, mode), verbose=True)
    grading(svc.predict(X), YVectorQ(stories, solutions, mode), verbose=True)

    # Plot
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))
    Z = svc.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    plt.contourf(xx, yy, Z, cmap=plt.cm.Paired, alpha=0.8)
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.Paired)

    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())
    plt.xticks(())
    plt.yticks(())
    plt.show()

if __name__ == "__main__":
    testset = "mc160.dev"
    stories = list(storyparser(testset))
    solutions = list(answers(testset))
    mode = Question.SINGLE

    svm_qa(stories, solutions, mode=mode)
