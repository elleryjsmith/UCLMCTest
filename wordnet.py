from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

posmap = { "R" : wn.ADV,
           "N" : wn.NOUN,
           "J" : wn.ADJ,
           "V" : wn.VERB }

lemmatizer = WordNetLemmatizer()

def wnpos(stanfordpos):
    
    if stanfordpos in posmap:
        return posmap[stanfordpos]
    else:
        return ""

def getlemma(word, stanfordpos):

    if not wnpos(stanfordpos):
        return word

    return lemmatizer.lemmatize(word,wnpos(stanfordpos))

wnmap = dict()

class WNToken(object):

    def __init__(self, synset):

        self.synset = synset
        #self.lemmas = []
        self.hypernyms = []

    @staticmethod
    def synsets(token):

        tpos = wnpos(token.mainpos())

        if not tpos or token.isproper():
            return []

        syns = [WNToken.fromsynset(s) for s in wn.synsets(token.token,tpos)]

        return {n:d for syn in syns
                for s,d in syn.dfs()
                for n in s.lexname().split(" ")}
                
    @staticmethod
    def fromsynset(synset):

        if synset.name() not in wnmap:
            wnmap[synset.name()] = WNToken(synset.name())
            
        wnt = wnmap[synset.name()]

        if not wnt.hypernyms:
            for hye in synset.hypernyms():
                wnt.hypernyms.append(WNToken.fromsynset(hye))
                
        #for lma in synset.lemmas():
        #    wnt.lemmas.append(lma.name())

        return wnt

    @staticmethod
    def fromcache(entry):

        wnt = WNToken(entry["synset"])

        #wnt.lemmas = entry["lemmas"]       
        wnt.hypernyms = [WNToken.fromcache(h) for h in entry["hypernyms"]]

        return wnt


    def depthof(self, name, pos="", stanford=False):

        if stanford:
            pos = wnpos(pos)
            if not pos:
                return 0
        
        for h in self.hypernyms:

            if h.lexname() == name and (not pos or pos == h.pos()):
                return 1;
            else:
                d = h.depthof(name,pos)
                if d:
                    return d + 1

        return 0

    def depthofsyn(self, synset):

        return self.depthof(synset.lexname(),synset.pos())
    
    def lowestdepth(self):

        return 1 + max([h.lowestdepth() for h in self.hypernyms] + [-1])
        
    def contains(self, name, pos="", stanford=False):

        if stanford:
            pos = wnpos(pos)
            if not pos:
                return False        

        for h in self._elems():
            if h.lexname() == name and (not pos or pos == h.pos()):
                return True

        return False

    def tree(self):

        return [self] + [h.tree() for h in self.hypernyms]

    def dfs(self):

        return self._dfs(0)
        
    def _dfs(self, depth):
        
        s = [(self,depth)]

        for h in self.hypernyms:
            s.extend(h._dfs(depth + 1))

        return s

    def _elems(self):

        s = {self}

        for h in self.hypernyms:
            s |= h._elems()

        return s
            
    def highestcommon(self, other):

        return min(self.pairs(other) or [(None,-1)],key=lambda x:x[1])

    def lowestcommon(self, other):

        return max(self.pairs(other) or [(None,-1)],key=lambda x:x[1])

    def pairs(self, other):

        return [(a,self.depthofsyn(a) + other.depthofsyn(a)) for a in (self._elems() & other._elems())]

    def lexname(self):
        
        return self.synset.split(".")[0].replace("_"," ")

    def pos(self):

        return self.synset.split(".")[1]

    def sense(self):

        return int(self.synset.split(".")[2])


    def parserepr(self):

        return {"synset":self.synset,"lemmas":self.lemmas,"hypernyms":[s.parserepr() for s in self.hypernyms]}


    def __eq__(self, other):
        
        return isinstance(other,self.__class__) and self.synset == other.synset

    def __ne__(self, other):

        return not self.__eq__(other)

    def __hash__(self):

        return hash(self.synset)
            
    def __str__(self):

        return "Name: %s\nHypernyms: %s\n" % (self.synset,self.hypernyms)

    def __repr__(self):

        return "WNToken(%r)" % (self.synset)
