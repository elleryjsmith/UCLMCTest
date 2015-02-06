from __future__ import with_statement
import cPickle as pickle
import csv
import os
from collections import deque

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

    def __init__(self):
        self.tokens = None
        self.lemma = []
        self.root = None

    @staticmethod
    def fromcache(entry):
        sp = SentenceParse()
        sp.tokens = dict([(i,Token.fromcache(e)) for i,e in entry["tokens"]])
        sp.tokens[0].wordindex = 0
        for i,t in enumerate([t for _,t in sp.tokens.items() if t.isword()]):
            t.wordindex = i
        sp.root = sp.tokens[0]
        sp.lemma = [t.tagged() for i,t in sp.tokens.items()]
        sp._unpackdeps(entry["dependencies"])
        sp._unpacktree(entry["tree"])
        return sp

    def words(self):

        return dict([(t.wordindex,t) for _,t in self.tokens.items() if t.isword()])

    def _packdeps(self):
        
        return [(g.index,d.index,r) for g,d,r in self.depgraph()]

    def _unpackdeps(self, deps):
        
        for g,d,r in deps:

            self.tokens[g].deplink(self.tokens[d],r)

    def depgraph(self):

        return self._deptrv(self.root)

    def _deptrv(self, node):

        res = []
        
        node.vis ^= 1
        
        for ch,_ in node.dependents:
            
            if ch.vis ^ node.vis:
                
                res.extend(self._deptrv(ch))

        res.extend([(g,node,r) for g,r in node.governers])

        return res

    def parsetree(self, mode="depth"):
        
        return self.root.parsetree(mode)

    def _packtree(self):

        return [(p.index,c.index) for l in self.root._parsedfs(self._parserel) for p,c in l]

    def _parserel(self, node):

        return [(p,node) for p in node.parents]

    def _unpacktree(self, nodes):

        for p,c in nodes:
            
            self.tokens[p].treelink(self.tokens[c])

    def parserepr(self):
        return {
            "tree": self._packtree(),
            "tokens": [(i,t.parserepr()) for i,t in self.tokens.items()],
            "dependencies": self._packdeps()
        }

    def __repr__(self):
        return "SentenceParse(%r)" % (self.tree)

    def __str__(self):
        return "Parse Tree:\n\n" + str(self.tree) + "\n\nTokens:\n\n" + str(self.tokens) + "\n\n"


class Token(object):


    def __init__(self, token, lemma, pos, index):

        self.token = token
        self.lemma = lemma
        self.pos = pos
        self.wordindex = -1
        self.children = []
        self.parents = []
        self.governers = []
        self.dependents = []
        self.vis = 0
        self.index = index
        self.synset = None

    @staticmethod
    def fromcache(entry):

        return Token(entry["token"],entry["lemma"],entry["pos"],entry["index"])

    def tagged(self):
        
        return (self.token,self.lemma,self.pos)

    def treelink(self, child):
        
        self.children.append(child)
        child.parents.append(self)

    def deplink(self, dependent, rel):

        self.dependents.append((dependent,rel))
        dependent.governers.append((self,rel))

    def isword(self):

        return self.token or False

    def subtree(self, tag, mode="depth"):

        for n in self._parsebfs():

            if not n.token and n.pos == tag and n is not self:
                
                return n.parsetree(mode)

    def parsetree(self, mode="depth"):
        
        return list(self._parsebfs() if mode == "breadth" else self._parsedfs())

    def _parsebfs(self, fn=lambda x: x):

        yield self

        q = deque([self])

        while q:

            for c in q.popleft().children:

                q.append(c)
    
                yield fn(c)
        

    def _parsedfs(self, fn=lambda x: x):
        
        s = [self]

        while s:

            yield fn(s[-1])

            for c in reversed(s.pop().children):
            
                s.append(c)


    def parserepr(self):

        return {"token":self.token,"lemma":self.lemma,"pos":self.pos,"index":self.index}

    def __str__(self):

        return str(self.tagged())

    def __repr__(self):

        return "Token(%r,%r,%r,%r)" % (self.token,self.lemma,self.pos,self.index)


def answers(stories):
    dataset = os.path.abspath(os.path.dirname(__file__) + "/datasets/" + stories + ".ans");
    with open(dataset, "r") as fl:
        soln = csv.reader(fl, delimiter='\t')

        for rw in soln:
            yield rw


def storyparser(stories):
    dataset = os.path.abspath(os.path.dirname(__file__) + "/datasets/" + stories + ".prs");
    with open(dataset, "r") as fl:
        strys = pickle.load(fl)
    for ln in strys:
        yield Story.fromcache(ln)
            

