import statementgenerator.lm as lm
import statementgenerator.rules as rules
import classes
import csv
from sys import argv, stderr

lmodel = lm.instantiateLM()

class qastory(object):

	def __init__(self, questions):
		self.questions = questions
		

class qaquestion(object):

	def __init__(self, question, answers, qastatements):
		self.question = question
		self.answers = answers
		self.qastatements = qastatements



def getmcteststatements(qalist, dataset, storyno, questionno):
	with open("datasets/statements/" + dataset + ".statements.tsv","r") as fl:
				mc = csv.reader(fl, delimiter='\t')
  				for index, row in enumerate(mc):
  					if index == storyno:
						for i, qa in enumerate(qalist):
							qa.append(row[4+questionno*5+i])



def generatestatements(dataset, storyno, story):
	questions = []
	for questionno, q in enumerate(story.questions):
		qalist = [[],[],[],[]]
		getmcteststatements(qalist, dataset, storyno, questionno)
		if str(q).startswith("Q: Who"):
			rules.generatewhostatements(qalist, q)
			
		finallist = []
		for answers in qalist:
			finallist.append(lm.lmfilter(lmodel, answers)) 
		question = qaquestion(str(q), [str(a) for a in q.answers], finallist)
		questions.append(question)


	storyobj = qastory(questions)

	return storyobj
	
def savetofile(dataset, stories):
	with open("datasets/generatedstatements/" + dataset + ".statementgen.tsv", "w") as fl:
		mc = csv.writer(fl, delimiter='\t')
		for i, story in enumerate(stories):
			row = [dataset + "." + str(i)]
			for q in story.questions:
				row.extend(q.qastatements)
			mc.writerow(row)

def qagenerate(dataset):
	qastories =[]
	storygen = classes.storyparser(dataset)
	for i, story in enumerate(storygen):
		storyobj = generatestatements(dataset, i, story)
		qastories.append(storyobj)
	savetofile(dataset, qastories)
	return qastories




if __name__ == "__main__":

    if len(argv) == 2:

        qagenerate(argv[1])

    else:

        stderr.write("Usage: python %s <dataset> (e.g. mc160.dev)\n" % (argv[0]))






