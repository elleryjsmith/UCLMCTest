from __future__ import with_statement
import csv
import sys
from edu.stanford.nlp.process import DocumentPreprocessor, PTBTokenizer, WordTokenFactory, Morphology
from edu.stanford.nlp.parser.lexparser import LexicalizedParser, Options
from edu.stanford.nlp.ling import WordTag
from edu.stanford.nlp.trees import TreePrint
from java.io import StringReader

stopwords = []


class Story:

    def __init__(self, sentences, questions, parser):
        self.sentences = sentences
        self.questions = questions
        self.parser = parser

    @staticmethod
    def fromdata(data, parser):
        stry = Story([], [], parser)
        txt = data[2].replace("\\newline", " ")
        stry.sentences = stry._extractsentences(txt)
        qdat = data[3:]

        for i in range(0, len(qdat), 5):
            stry.questions.append(Question.fromdata(qdat[i:i + 5], parser))

        return stry

    @staticmethod
    def fromcache(entry):
        return Story(
            [Sentence.fromcache(s) for s in entry["sentences"]],
            [Question.fromcache(q) for q in entry["questions"]],
            None
        )

    def __repr__(self):
        return "Story(%r,%r,%r)" % (self.sentences, self.questions, self.parser)

    def __str__(self):
        s = "Story text:\n\n" + "".join([str(s) for s in self.sentences])
        return s + "\n\nQuestions:\n\n" + "".join([str(q) for q in self.questions])

    def parserepr(self):
        return {
            "sentences": [s.parserepr() for s in self.sentences],
            "questions": [q.parserepr() for q in self.questions]
        }

    def _extractsentences(self, text):
        snts = []
        for snt in DocumentPreprocessor(StringReader(text)):
            s = Sentence(snt, self.parser)
            s.parse = s._parse()
            snts.append(s)

        return snts


class Sentence:

    def __init__(self, tokens, parser):
        self.tokens = tokens
        self.parser = parser
        self.parse = None

    @staticmethod
    def fromstring(string, parser):
        tkns = PTBTokenizer(StringReader(string), WordTokenFactory(), "").tokenize()
        s = Sentence(tkns, parser)
        s.parse = s._parse()
        return s

    @staticmethod
    def fromcache(entry):
        s = Sentence(entry["tokens"], None)
        s.parse = SentenceParse.fromcache(entry["parse"])
        return s

    def _parse(self):
        return self.parser.apply(self)

    def parserepr(self):
        return {
            "string": str(self),
            "tokens": [repr(t) for t in self.tokens],
            "parse": self.parse.parserepr()
        }

    def __repr__(self):
        return "Sentence(%r,%r)" % (self.tokens, self.parser)

    def __str__(self):
        return "".join([" " + str(t) if str(t) not in ".,:;!?" else str(t) for t in self.tokens])

    def printtree(self, style="penn"):
        TreePrint(style).printTree(self.parse.tree)

    def printlemma(self):
        for w, l, p in self.parse.lemma:
            print w, l, p


class Question:
    MULTIPLE = 0
    SINGLE = 1

    def __init__(self, mode, qsentence, answers, parser):
        self.mode = mode
        self.qsentence = qsentence
        self.answers = answers
        self.parser = parser

    @staticmethod
    def fromdata(data, parser):
        qstr = data[0].split(":")
        mode = Question.MULTIPLE if qstr[0] == "multiple" else Question.SINGLE
        qn = Question(mode, Sentence.fromstring(qstr[1], parser), [], parser)

        for ans in data[1:]:
            qn.answers.append(Sentence.fromstring(ans, parser))

        return qn

    @staticmethod
    def fromcache(entry):
        return Question(
            entry["mode"],
            Sentence.fromcache(entry["question"]),
            [Sentence.fromcache(a) for a in entry["answers"]],
            None
        )

    def __repr__(self):
        return "Question(%r,%r,%r,%r)" % (self.mode, self.qsentence, self.answers, self.parser)

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


class Parser:

    def __init__(self, path, options=[], debug=False):
        self.path = path
        self.debug = debug
        self.opt = options

        self.options = Options()
        self.options.setOptions(options)

        self.morphology = Morphology()
        self.parser = LexicalizedParser.getParserFromFile(self.path, self.options)

    def apply(self, sentence):
        if self.debug:
            sys.stderr.write("Parsing sentence: \"%s\"\n" % (sentence))
        return SentenceParse.fromtree(self, self.parser.apply(sentence.tokens))

    def __repr__(self):
        return "Parser(%r,%r,%r)" % (self.path, self.opt, self.debug)


class SentenceParse:

    def __init__(self, parser, tree):
        self.parser = parser
        self.tree = tree
        self.lemma = None

    @staticmethod
    def fromtree(parser, tree):
        sp = SentenceParse(parser, tree)
        sp.lemma = sp._lemmatize()
        return sp

    def _lemmatize(self):
        return self._dfs(self.tree, self._wordlemma)

    def _wordlemma(self, word, pos):
        wt = WordTag(word.value(), pos.value())
        return (word.value(), self.parser.morphology.lemmatize(wt).lemma(), pos.value())

    def _dfs(self, tree, fn):
        if tree.isPreTerminal():
            return [fn(tree.children()[0], tree)]
        else:
            clst = []
            for c in tree.children():
                clst.extend(self._dfs(c, fn))
        return clst

    @staticmethod
    def fromcache(entry):
        sp = SentenceParse(None, entry["tree"])
        sp.lemma = entry["lemma"]
        return sp

    def parserepr(self):
        return {
            "tree": repr(self.tree),
            "lemma": self.lemma
        }

    def __repr__(self):
        return "SentenceParse(%r,%r)" % (self.parser, self.tree)

    def __str__(self):
        return "Parse Tree:\n\n" + str(self.tree) + "\n\nLemmatization:\n\n" + str(self.lemma) + "\n\n"


def similarity(s1, s2):
    sim = []
    for w1, l1, p1 in s1:
        if w1 in stopwords or l1 in stopwords:
            continue

        for w2, l2, p2 in s2:
            if w2 in stopwords or l2 in stopwords:
                continue
            elif l2 == l1:
                sim.append((w1, l1, p1))
                break
    return sim


def answers(stories):
    with open("MCTest/" + stories + ".ans", "r") as fl:
        soln = csv.reader(fl, delimiter='\t')

        for rw in soln:
            yield rw


def storyparser(stories, parsefile="", options=[], debug=False):
    global stopwords
    with open("MCTest/stopwords.txt", "r") as fl:
        txt = fl.read()
    stopwords = txt.split('\r\n')

    if parsefile != "":
        parser = Parser(parsefile, options, debug)

        with open("MCTest/" + stories + ".tsv", "r") as fl:
            mc = csv.reader(fl, delimiter='\t')
            for rw in mc:
                yield Story.fromdata(rw, parser)
    else:
        with open("MCTest/" + stories + ".prs", "r") as fl:
            for ln in fl:
                yield Story.fromcache(eval(ln))
