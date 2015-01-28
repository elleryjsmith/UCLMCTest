# Training set
import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm
from classifiers.perceptron import Perceptron
from classes import storyparser, answers
from features import bow

def YVector(solutions):
    Y = []
    for story, solution in zip(stories, solutions):
        for q, question in enumerate(story.questions):
            solution_n = int(solution[q].encode("hex")) - 41 # From A to 0
            correct_answers = [int(a == solution_n) for a, _ in enumerate(question.answers)]
            Y = Y + correct_answers
    return Y

testset = "mc160.dev"
stories = list(storyparser(testset))
solutions = list(answers(testset))

X = np.array(zip(
    bow.XVector(stories, norm="all"),
    bow.XVector(stories, norm="question")
))
y = np.array(YVector(solutions))


h = .01
C = 4.0
svc = svm.SVC(kernel='linear', C=C).fit(X, y)

x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                     np.arange(y_min, y_max, h))

Z = svc.predict(np.c_[xx.ravel(), yy.ravel()])


Z = Z.reshape(xx.shape)
plt.contourf(xx, yy, Z, cmap=plt.cm.Paired, alpha=0.8)


plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.Paired)
plt.xlabel('F1 Bag of words normalized overall')
plt.ylabel('F2 Bag of words normalized per question')
plt.xlim(xx.min(), xx.max())
plt.ylim(yy.min(), yy.max())
plt.xticks(())
plt.yticks(())

plt.show()
