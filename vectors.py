from sklearn.metrics import accuracy_score
import numpy as np


def results(X, Y, verbose=False):
    # vector of all question scores [[0.11,0.88,0.12,0.9],[0.2...]]
    predicted_q = np.split(np.asarray(X), len(X) / 4)
    # (answer_number, isItPredicted?)
    predicted_a = map(lambda x: (np.argmax(x), x[np.argmax(x)], x), predicted_q)
    # remove the ones that have been guessed
    x_answered = []
    y_answered = []
    for i, pred in enumerate(predicted_a):
        # pred[1] is the confidence, if it is 0, then it is a random guess
        if pred[2].tolist().count(pred[1]) != 1:
            continue
        if pred[1] != 0:
            x_answered.append(Y[i])
            y_answered.append(pred[0])

    if verbose:
        print "\n### Results ###"
        print "# questions   " + str(len(X)/4)
        print "# answered   " + str(len(x_answered))
        print "# correct   " + str(accuracy_score(y_answered, x_answered, normalize=False))
        print "% correct   " + str(accuracy_score(y_answered, x_answered))
        print ""
    return x_answered, y_answered


def YVectorQA(stories, solutions, mode=None):
    Y = []
    for story, solution in zip(stories, solutions):
        for q, question in enumerate(story.questions):
            if mode and question.mode != mode:
                continue
            solution_n = int(solution[q].encode("hex")) - 41 # From A to 0
            correct_answers = [int(a == solution_n) for a, _ in enumerate(question.answers)]
            Y = Y + correct_answers
    return Y


def YVectorQ(stories, solutions, mode=None):
    Y = []
    for story, solution in zip(stories, solutions):
        for q, question in enumerate(story.questions):
            if mode and question.mode != mode:
                continue
            solution_n = int(solution[q].encode("hex")) - 41 # From A to 0
            Y.append(solution_n)
    return Y
