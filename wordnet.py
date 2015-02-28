from nltk.corpus import wordnet as wn
from classes import Token

posmap = { "R" : wn.ADV,
           "N" : wn.NOUN,
           "J" : wn.ADJ,
           "V" : wn.VERB }

def wnpos(stanfordpos):
    
    if stanfordpos in posmap:
        return posmap[stanfordpos]
    else:
        return ""

class WNToken(object):

    def __init__(self, synset):

        self.synset = synset
        self.lemmas = []
        self.hypernyms = []

    @staticmethod
    def synsets(token):

        tpos = wnpos(token.mainpos())

        if not tpos or token.isproper():
            return []

        return [WNToken.fromsynset(s) for s in wn.synsets(token.token,tpos)]

    @staticmethod
    def fromsynset(synset):
     
        wnt = WNToken(synset.name())

        for hye in synset.hypernyms():
            wnt.hypernyms.append(WNToken.fromsynset(hye))
                
        for lma in synset.lemmas():
            wnt.lemmas.append(lma.name())

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

    def _elems(self):

        s = {self}

        for h in self.hypernyms:
            s |= h._elems()

        return s
            
    def lowestcommon(self, other):

        return min([(a,self.depthof(a.lexname(),pos=a.pos()) + other.depthof(a.lexname(),pos=a.pos())) for a in (self._elems() & other._elems())],key=lambda x:x[1])[0]

    def lexname(self):
        
        return self.synset.split(".")[0]

    def pos(self):

        return self.synset.split(".")[1]

    def __eq__(self, other):
        
        return self.synset == other.synset

    def __ne__(self, other):

        return not self.__eq__(other)

    def __hash__(self):

        return hash(self.synset)
            
    def __str__(self):

        return "Name: %s\nHypernyms: %s\nLemmas: %s\n" % (self.synset,self.hypernyms,self.lemmas)

    def __repr__(self):

        return "WNToken(%r)" % (self.synset)
