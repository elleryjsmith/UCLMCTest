from __future__ import with_statement

import csv


class Story(object):

    def __init__(self, sentences, questions):
        self.sentences = sentences
        self.questions = questions

    @staticmethod
    def fromcache(entry):
        return Story(
            [Sentence.fromcache(s) for s in entry["sentences"]],
            [Question.fromcache(q) for q in entry["questions"]],
        )

    def __repr__(self):
        return "Story(%r,%r)" % (self.sentences, self.questions)

    def __str__(self):
        s = "Story text:\n\n" + "".join([str(s) for s in self.sentences])
        return s + "\n\nQuestions:\n\n" + "".join([str(q) for q in self.questions])

    def parserepr(self):
        return {
            "sentences": [s.parserepr() for s in self.sentences],
            "questions": [q.parserepr() for q in self.questions]
        }

class Sentence(object):

    def __init__(self, tokens):
        self.tokens = tokens
        self.parse = None

    @staticmethod
    def fromcache(entry):
        s = Sentence(entry["tokens"])
        s.parse = SentenceParse.fromcache(entry["parse"])
        return s

    def parserepr(self):
        return {
            "string": str(self),
            "tokens": [repr(t) for t in self.tokens],
            "parse": self.parse.parserepr()
        }

    def __repr__(self):
        return "Sentence(%r)" % (self.tokens)

    def __str__(self):
        return "".join([" " + str(t) if str(t) not in ".,:;!?" else str(t) for t in self.tokens])

    def printlemma(self):
        for w, l, p in self.parse.lemma:
            print w, l, p


class Question(object):
    MULTIPLE = 0
    SINGLE = 1

    def __init__(self, mode, qsentence, answers):
        self.mode = mode
        self.qsentence = qsentence
        self.answers = answers

    @staticmethod
    def fromcache(entry):
        return Question(
            entry["mode"],
            Sentence.fromcache(entry["question"]),
            [Sentence.fromcache(a) for a in entry["answers"]],
        )

    def __repr__(self):
        return "Question(%r,%r,%r)" % (self.mode, self.qsentence, self.answers)

    def __str__(self):
        s = "Q:%s\n\n" % (self.qsentence)
        s += "\n".join(["A%d:%s" % (i, a) for i, a in enumerate(self.answers)])

        return s + "\n\n"

    def parserepr(self):

        return {
            "mode": self.mode,
            "question": self.qsentence.parserepr(),
            "answers": [a.parserepr() for a in self.answers]
        }

class SentenceParse(object):

    def __init__(self, tree):
        self.tree = tree
        self.lemma = None

    @staticmethod
    def fromcache(entry):
        sp = SentenceParse(entry["tree"])
        sp.lemma = entry["lemma"]
        return sp

    def parserepr(self):
        return {
            "tree": repr(self.tree),
            "lemma": self.lemma
        }

    def __repr__(self):
        return "SentenceParse(%r)" % (self.tree)

    def __str__(self):
        return "Parse Tree:\n\n" + str(self.tree) + "\n\nLemmatization:\n\n" + str(self.lemma) + "\n\n"


def answers(stories):
    with open("datasets/" + stories + ".ans", "r") as fl:
        soln = csv.reader(fl, delimiter='\t')

        for rw in soln:
            yield rw


def storyparser(stories):
    with open("datasets/" + stories + ".prs", "r") as fl:
        for ln in fl:
            yield Story.fromcache(eval(ln))


