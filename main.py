from classes import storyparser, answers, loadOrPredict
from grading import grading
from vectors import results, YVectorQ
from features import bow
import classifier as svm
import logistic_regression as logreg

testsets = [
    "mc160.dev",
    "mc500.dev",
    "mc160.train",
    "mc500.train",
    ["mc160.dev", "mc160.train"],
    ["mc500.dev", "mc500.train"]
]

methods = [
    dict(
        name="Baseline (BOW)",
        score=bow.predict,
        opts=dict(
            testsets=testsets,
            pickle=True
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
            testsets=["mc160.dev"],
            features=[bow.predict]
        )
    ),
    dict(
        name="SVM (BOW) train mc500train",
        score=svm.predict,
        opts=dict(
            trainsets=["mc500.train"],
            testsets=["mc500.dev"],
            features=[bow.predict]
        )
    ),
    dict(
        name="SVM (BOW+BOWall) train mc160train",
        score=svm.predict,
        opts=dict(
            trainsets=["mc160.train"],
            testsets=["mc160.dev"],
            features=[bow.predict, bow.predictAll]
        )
    ),
    dict(
        name="SVM (BOW+BOWall) train mc500train",
        score=svm.predict,
        opts=dict(
            trainsets=["mc500.train"],
            testsets=["mc500.dev"],
            features=[bow.predict, bow.predictAll]
        )
    ),
    dict(
        name="LogReg (BOW+BOWall) mc160train",
        score=logreg.predict,
        opts=dict(
            trainsets=["mc160.train"],
            testsets=["mc160.dev"]
        )
    ),
    dict(
        name="LogReg (BOW+BOWall) mc500train",
        score=logreg.predict,
        opts=dict(
            trainsets=["mc500.train"],
            testsets=["mc500.dev"]
        )
    )
]

results = {}
for method in methods:
    results[method["name"]] = {}
    for testset in testsets:
        results[method["name"]][str(testset)] = "0"

for method in methods:
    name = method["name"]

    for testset in method["opts"]["testsets"]:
        stories = list(storyparser(testset))
        solutions = list(answers(testset))
        true = YVectorQ(stories, solutions)
        scores = loadOrPredict(method, stories, method["opts"], pickle_label=str(testset))
        grades = grading(scores, true)
        results[name][str(testset)] = sum(grades) / len(grades)
        print results[name][str(testset)]

print "\n"
print "| Description | " + " | ".join([str(x) for x in testsets]) + " |"
print "| " + ("--- | ---" * len(testsets)) + " |"
for method in methods:
    m_results = [results[method["name"]][str(t)] for t in testsets]
    print "| %s | %s |" % (
        method["name"],
        " | ".join([str(r) for r in m_results])
    )
