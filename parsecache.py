from __future__ import with_statement
from storyparser import storyparser

testset = "mc500.dev"
parserfile = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
stories = storyparser(testset, parserfile, debug=True)

with open("datasets/" + testset + ".prs", "w") as fl:
    fl.write("\n".join([repr(story.parserepr()) for story in stories]))
