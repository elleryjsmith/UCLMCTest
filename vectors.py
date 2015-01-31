from sklearn.metrics import accuracy_score
import numpy as np
from itertools import groupby


def results(X, Y, verbose=False, ambiguity=0):
    # vector of all question scores [[0.11,0.88,0.12,0.9],[0.2...]]
    predicted_q = np.split(np.asarray(X), len(X) / 4)
    # (answer_number, isItPredicted?)
    predicted_a = map(lambda x: (np.argmax(x), x[np.argmax(x)]), predicted_q)
    # remove the ones that have been guessed
    x_answered = []
    y_answered = []
    for i, pred in enumerate(predicted_a):
        # pred[1] is the confidence, if it is 0, then it is a random guess
        if pred[1] != ambiguity:
            x_answered.append(Y[i])
            y_answered.append(pred[0])

    if verbose:
        print "\n### Results ###"
        print "# questions   " + str(len(X)/ 4)
        print "# answered   " + str(len(x_answered))
        print "# correct   " + str(accuracy_score(y_answered, x_answered, normalize=False))
        print "% correct   " + str(accuracy_score(y_answered, x_answered))
        print ""
    return x_answered, y_answered


def orderby_score(answer_set):
    answer_sorted = [(a, answer_set[a]) for a in np.argsort(answer_set, axis=0)[::-1]]
    groups = groupby(answer_sorted, lambda x: answer_set[x[0]])
    answer_groups = ((k, [j[0] for j in g]) for k, g in groups)
    return list(answer_groups)


def grading(X, Y, verbose=False):
    # vector of all question answers [[0.11,0.88,0.12,0.9],[0.2...]]
    answer_sets = np.split(np.asarray(X), len(X) / 4)
    # questions divided by group of score [[(0.97,[0,1]), (0,[2,3])], ..]
    answer_sets_grouped = [orderby_score(a) for a in answer_sets]
    # the score is 1/(# groups till the answer + # equal answers)
    grades = []
    for story_i, answer_group in enumerate(answer_sets_grouped):
        for group_i, answer in enumerate(answer_group):
            if Y[story_i] in answer[1]:
                grades.append(1.0 / (group_i + len(answer[1])))
    return grades


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
