# Training set
import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm
from classifiers.perceptron import Perceptron
from classes import storyparser, answers, Question, results, YVectorQA, YVectorQ
from features import bow
from sklearn.metrics import accuracy_score


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


testset = "mc160.dev"
stories = list(storyparser(testset))
solutions = list(answers(testset))
mode = Question.SINGLE

svm_qa(stories, solutions, mode=mode)
