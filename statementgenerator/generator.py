import code
import readline
import rlcompleter
##################
import sys
sys.path.insert(0, '../')
import classes


def generatewhostatements(qalist, question):
	q = str(question.qsentence)
	q.replace("Who ", "", 1)
	q.replace("?", ".", 1)
	for i, answer in enumerate(question.answers):
		a = str(answer)
		concat = a + q
		qalist[i].append(concat)
	return qalist

def generatestatements(story):
	for q in story.questions:
		qalist = [[],[],[],[]]
		if str(q).startswith("Q: Who"):
			qageneratewhostatements(qalist, q)
			
		finallist = []
		for answers in qalist:
			finallist.append(lmfilter(answers)) 

	
def savetofile(filename, stories):
	with open("datasets/" + filename + ".prs", "w") as fl:
        pickle.dump([story.parserepr() for story in stories], fl)

def qagenerate(datasets):
	for dataset in datasets:
		newstories = []
		storygen = classes.storyparser(dataset)
		for story in storygen:
			newStory = generatestatements(story)
			filteredstories.add(newStory)
		savetofile(dataset + ".filtered", )








######################



vars = globals()
vars.update(locals())
readline.set_completer(rlcompleter.Completer(vars).complete)
readline.parse_and_bind("tab: complete")
shell = code.InteractiveConsole(vars)
shell.interact()




