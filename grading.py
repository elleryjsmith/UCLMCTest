import numpy as np
import matplotlib.pyplot as plt
from itertools import groupby


def orderby_score(answer_set):
    answer_sorted = [(a, answer_set[a]) for a in np.argsort(answer_set, axis=0)[::-1]]
    groups = groupby(answer_sorted, lambda x: answer_set[x[0]])
    answer_groups = ((k, [j[0] for j in g]) for k, g in groups)
    return list(answer_groups)


def grading(X, Y, verbose=False, detailed=False):
    # vector of all question answers [[0.11,0.88,0.12,0.9],[0.2...]]
    answer_sets = np.split(np.asarray(X), len(X) / 4)
    # questions divided by group of score [[(0.97,[0,1]), (0,[2,3])], ..]
    answer_sets_grouped = [orderby_score(a) for a in answer_sets]
    # the score is 1/(# groups till the answer + # equal answers)
    grades = []
    grades_detailed = []
    for story_i, answer_group in enumerate(answer_sets_grouped):
        for group_i, answer in enumerate(answer_group):
            if group_i == 0:
                if Y[story_i] in answer[1]:
                    grade = 1.0 / (group_i + len(answer[1]))
                    grades.append(grade)
                    if verbose or detailed:
                        grades_detailed.append(dict(
                            grade=grade,
                            equal=len(answer[1]),
                            group=group_i,
                            score=answer[0]
                        ))
            else:
                if Y[story_i] in answer[1]:
                    grades.append(0)
                    if verbose or detailed:
                        grades_detailed.append(dict(
                            grade=0,
                            equal=len(answer[1]),
                            group=group_i,
                            score=answer[0]
                        ))

    if verbose:
        grades_sorted = sorted(grades_detailed, key=lambda x: x["grade"])
        groups = groupby(grades_sorted, lambda x: x["grade"])
        grades_grouped = list((k, list(g)) for k, g in groups)
        print "### Grading ###"
        print "# questions", len(grades)
        for group in grades_grouped:
            print "# partial credit (%lF) %i" % (group[0], len(group[1]))
        print "# Total grade", sum(grades) / len(grades)
        print ""
    if detailed:
        return grades_detailed
    return grades
