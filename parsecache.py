from __future__ import with_statement
from stanfordclasses import JStory, JParser
from csv import reader as csvreader
from sys import argv, stderr
import cPickle as pickle


def storyparser(stories, parsefile, options=[], debug=False):


    parser = JParser(parsefile,options,debug)


    with open("datasets/" + stories + ".tsv","r") as fl:

        mc = csvreader(fl,delimiter='\t')

        for rw in mc:

            yield JStory.fromdata(rw,parser)



if __name__ == "__main__":

    if len(argv) == 2:

        testset = argv[1]

        parserfile = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"

        options = ["-outputFormat","typedDependencies","-retainTmpSubcategories"]

        stories = storyparser(testset,parserfile,options,True)

        with open("datasets/" + testset + ".prs", "w") as fl:

            pickle.dump([story.parserepr() for story in stories],fl)

    else:

        stderr.write("Usage: jython %s <testset> (e.g. mc160.dev)\n" % (argv[0]))
