from classes import storyparser, answers
from grading import grading
from vectors import results, YVectorQ
from features import bow
import classifier as svm

testsets = [
    "mc160.dev",
    "mc500.dev",
    "mc160.train",
    "mc500.train"
]

methods = [
    dict(
        name="Baseline (BOW)",
        score=bow.predict,
        opts=dict(
            testsets=testsets
        )
    ),
    dict(
        name="Baseline (BOW) all",
        score=bow.predictAll,
        opts=dict(
            testsets=testsets
        )
    ),
    dict(
        name="SVM (BOW) train mc160train",
        score=svm.predict,
        opts=dict(
            trainsets=["mc160.train"],
            testsets=["mc160.dev", "mc500.dev"]
        )
    ),
    dict(
        name="SVM (BOW) train mc500train",
        score=svm.predict,
        opts=dict(
            trainsets=["mc500.train"],
            testsets=["mc160.dev", "mc500.dev"]
        )
    )
]

results = {}
for method in methods:
    results[method["name"]] = {}
    for testset in testsets:
        results[method["name"]][testset] = "0"

for method in methods:
    name = method["name"]

    for testset in method["opts"]["testsets"]:
        stories = list(storyparser(testset))
        solutions = list(answers(testset))
        true = YVectorQ(stories, solutions)
        scores = method["score"](stories, method["opts"])
        grades = grading(scores, true)
        results[name][testset] = sum(grades) / len(grades)
        print results[name][testset]

print "\n"
print "| Description | " + " | ".join(testsets) + " |"
print "| " + ("--- | ---" * len(testsets)) + " |"
for method in methods:
    m_results = [results[method["name"]][t] for t in testsets]
    print "| %s | %s |" % (
        method["name"],
        " | ".join([str(r) for r in m_results])
    )
