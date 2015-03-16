from scoring import bowall
from modifiers import negtokens, propersubject, subclauses, tempmods

class Filter(object):

    def __init__(self, condition, function):

        self.condition = condition
        self.function = function
        self.processed = []
        self.curr = 0

    def apply(self, q, a, story):

        self.processed.append({"filtered":True,"q":q,"a":a,"story":story})

        if not self.condition or self.condition(q,a,story):            
            self.function(q,a,story)
            self.processed[-1]["state"] = [t for s in story.sentences
                                           for t in s.wbow.values()]
        else:
            self.processed[-1]["filtered"] = False

    def addscores(self, scores, grade):

        for s in scores:
            self.processed[self.curr]["score"] = s
            self.processed[self.curr]["grade"] = grade
            self.curr += 1

    def stats(self):

        return (("# Filter %s -> %s\n"
                 "Total questions processed: %d\n"
                 "%s\nOverall grade: %f%%")
                % (self.condition.__name__ if self.condition else "all",
                   self.function.__name__,
                   len(self.processed) / 4,
                   self.gradeans(),
                   self.grade()))

    def gradeans(self):

        st = [("All",(self.filteredans(),self.processed)),
              ("Correct",(self.correctans(),self.filteredans())),
              ("Ambiguous",(self.ambiguousans(),self.filteredans())),
              ("Incorrect",(self.incorrectans(),self.filteredans()))]
        
        return "\n".join([("%s filtered questions: %d (%f%%)"
                           % (s,len(f[0])/4,
                              (len(f[0])*100.0/len(f[1]))
                              if f[1] else 0))
                          for s,f in st])
    
    def filteredans(self):
        return [a for a in self.processed
                if a["filtered"]]

    def correctans(self):
        return [a for a in self.processed
                if a["grade"] == 1 and a["filtered"]]

    def ambiguousans(self):
        return [a for a in self.processed
                if a["grade"] > 0 and a["grade"] < 1 and a["filtered"]]

    def incorrectans(self):
        return [a for a in self.processed
                if a["grade"] == 0 and a["filtered"]]

    def grade(self):

        f = [a["grade"] for a in self.processed if a["filtered"]]

        return sum(f) * 100.0 / len(f)

    def comparison(self, other, state=False):

        yield "%s\n%s" % (self.stats(),other.stats())

        for i in range(0,len(self.processed),4):
            if not self.processed[i]["filtered"]:
                continue
            yield ("###\n\n%s\n\n%s\n%s: %s (%f)\n%s: %s (%f)\n\n%s\n%s\n\n"
                   % (" ".join(map(str,self.processed[i]["story"].sentences)),
                      str(self.processed[i]["q"]),
                      self.function.__name__,
                      map(lambda x:x["score"],self.processed[i:i+4]),
                      self.processed[i]["grade"],
                      other.function.__name__,
                      map(lambda x:x["score"],other.processed[i:i+4]),
                      other.processed[i]["grade"],
                      "\n###\n%s\n%s\n" % (self.function.__name__,
                                           self.processed[i]["state"])
                      if state else "",
                      "\n###\n%s\n%s\n" % (other.function.__name__,
                                           other.processed[i]["state"])
                      if state else ""))

    def compare(self, other):

        c,sc,oc = 0.0,0.0,0.0

        for s,o in zip(self.processed,other.processed):
            if s["filtered"]:
                c += 0.25
                sc += s["grade"] / 4
                oc += o["grade"] / 4

        return ("Questions filtered by %s: %d (%f%%)\n"
                "Performance of %s: %f%%\n"
                "Performance of %s: %f%%\n"
                "Improvement: %f%%"
                % (self.condition.__name__ if self.condition else "all",
                   c,c * 400.0 / len(self.processed),
                   self.function.__name__,sc * 100.0 / c,
                   other.function.__name__,oc * 100.0 / c,
                   (sc - oc) * 100.0 / c))

    def reset(self):

        self.processed = []
        self.curr = 0

    def __repr__(self):

        return "Filter(%r,%r)" % (self.condition,self.function)


def simplenegative(q,a,story):

    if negatedquestion(q.qsentence):

        mnt = [(bowall(None,an,story),an) for an in q.answers]

        return len([m for m,an in mnt if not m]) == 1

def complexnegative(q,a,story):

    return negatedquestion(q.qsentence) and not simplenegative(q,a,story)

def nonnegative(q,a,story):

    return not negatedquestion(q.qsentence)

def nocharacter(q,a,story):

    return not propersubject(q.qsentence)

def contextual(q,a,story):

    return subclauses(q.qsentence)

def negatedquestion(q):

    return ({d for d,r in q.parse.headword().dependents if r == "neg"}
            and not ({w.lemma for w in q.words} & {"why","how"}))

def whyquestion(q,a,story):

    return "why" in [w.lemma for w in q.qsentence.words]

def tempquestion(q,a,story):

    return [t for t in q.qsentence.words if t.lemma == "before" or t.lemma == "after"]
