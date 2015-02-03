import sys
from classes import storyparser, Question, answers
from grading import grading
from vectors import results, YVectorQ
from features import bow
import classifier as svm
import numpy as np

testsets = [
    "mc160.dev"
    , "mc500.dev"
    , "mc160.train"
    , "mc500.train"
]

methods = [
    dict(name="Baseline (BOW) sentence", score=bow.predict, opts=None)
    , dict(name="Baseline (BOW) all", score=bow.predictAll, opts=None)
    , dict(name="SVM (only BOW)", score=svm.predict, opts=None)
]

results = {}
for method in methods:
    name = method["name"]
    results[name] = {}

    for testset in testsets:
        stories = list(storyparser(testset))
        solutions = list(answers(testset))
        true = YVectorQ(stories, solutions)

        scores = method["score"](stories, method["opts"])
        grades = grading(scores, true)
        results[name][testset] = sum(grades) / len(grades)

print "| Description | " + " | ".join(testsets) + " |"
print "| " + ("--- | ---" * len(testsets)) + " |"
for method in methods:
    m_results = [results[method["name"]][t] for t in testsets]
    print "| %s | %s |" % (
        method["name"],
        " | ".join([str(r) for r in m_results])
    )
