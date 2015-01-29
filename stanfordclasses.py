from __future__ import with_statement
import sys
import classes

from edu.stanford.nlp.process import DocumentPreprocessor, PTBTokenizer, WordTokenFactory, Morphology
from edu.stanford.nlp.parser.lexparser import LexicalizedParser, Options
from edu.stanford.nlp.ling import WordTag
from edu.stanford.nlp.trees import TreePrint
from java.io import StringReader


class JStory(classes.Story):

    def __init__(self, sentences, questions, parser):

        super(JStory,self).__init__(sentences,questions)

        self.parser = parser


    @staticmethod
    def fromdata(data, parser):

        stry = JStory([],[],parser)


        txt = data[2].replace("\\newline"," ")

        stry.sentences = stry._extractsentences(txt)


        qdat = data[3:]

        for i in range(0,len(qdat),5):

            stry.questions.append(JQuestion.fromdata(qdat[i:i+5],parser))


        return stry


    def __repr__(self):

        return "JStory(%r,%r,%r)" % (self.sentences,self.questions,self.parser)


    def _extractsentences(self, text):

        snts = []

        for snt in DocumentPreprocessor(StringReader(text)):

            s = JSentence(snt,self.parser)

            s.parse = s._parse()

            snts.append(s)


        return snts


class JSentence(classes.Sentence):

    def __init__(self, tokens, parser):

        super(JSentence,self).__init__(tokens)

        self.parser = parser


    @staticmethod
    def fromstring(string, parser):

        tkns = PTBTokenizer(StringReader(string),WordTokenFactory(),"").tokenize()

        s = JSentence(tkns,parser)

        s.parse = s._parse()

        return s


    def _parse(self):

        return self.parser.apply(self)

    def __repr__(self):

        return "JSentence(%r,%r)" % (self.tokens,self.parser)

    def printtree(self, style="penn"):

        TreePrint(style).printTree(self.parse.tree)


class JQuestion(classes.Question):

    def __init__(self, mode, qsentence, answers, parser):

        super(JQuestion,self).__init__(mode,qsentence,answers)
        
        self.parser = parser


    @staticmethod
    def fromdata(data, parser):

        qstr = data[0].split(":")

        mode = classes.Question.MULTIPLE if qstr[0] == "multiple" else classes.Question.SINGLE


        qn = JQuestion(mode,JSentence.fromstring(qstr[1],parser),[],parser)


        for ans in data[1:]:

            qn.answers.append(JSentence.fromstring(ans,parser))


        return qn


    def __repr__(self):
        return "JQuestion(%r,%r,%r,%r)" % (self.mode,self.qsentence,self.answers,self.parser)


class JParser:

    def __init__(self, path, options=[], debug=False):

        self.path = path
        self.debug = debug
        self.opt = options

        self.options = Options()
        self.options.setOptions(options)

        self.morphology = Morphology()
        self.parser = LexicalizedParser.getParserFromFile(self.path,self.options)

    def apply(self, sentence):

        if self.debug:

            sys.stderr.write("Parsing sentence: \"%s\"\n" % (sentence))

        return JSentenceParse.fromtree(self,self.parser.apply(sentence.tokens))


    def __repr__(self):

        return "JParser(%r,%r,%r)" % (self.path,self.opt,self.debug)


class JSentenceParse(classes.SentenceParse):

    def __init__(self, parser, tree):

        super(JSentenceParse,self).__init__(tree)

        self.parser = parser


    @staticmethod
    def fromtree(parser, tree):

        sp = JSentenceParse(parser,tree)

        sp.lemma = sp._lemmatize()

        return sp


    def _lemmatize(self):

        return self._dfs(self.tree,self._wordlemma)


    def _wordlemma(self, word, pos):

        wt = WordTag(word.value(),pos.value())

        return (word.value(),self.parser.morphology.lemmatize(wt).lemma(),pos.value())


    def _dfs(self, tree, fn):


        if tree.isPreTerminal():

            return [fn(tree.children()[0],tree)]

        else:

            clst = []

            for c in tree.children():

                clst.extend(self._dfs(c,fn))


        return clst



    def __repr__(self):

        return "JSentenceParse(%r,%r)" % (self.parser,self.tree)

