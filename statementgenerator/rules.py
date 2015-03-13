import enchant
from enchant.checker import SpellChecker

#Spell checker to ensure that words are properly spaced within statements
def spellcheck(sentence):
	checker = SpellChecker("en_US")
	checker.set_text(sentence)
	for error in checker:
		for suggestion in error.suggest():
			if error.word.replace(' ','') == suggestion.replace(' ',''):
				error.replace(suggestion)
				break
	return checker.get_text()


def generatewhostatements(qalist, question):
	q1 = str(question.qsentence)
	q2 = q1.replace("Who ", "", 1)
	qf = q2.replace("?", ".", 1)
	for i, answer in enumerate(question.answers):
		a = str(answer)
		concat = a + qf
		qalist[i].append(concat)
	return qalist

def generatereplacedfirstprp(qalist, question):
	nnp1 = None
	for i in question.qsentence.parse.tokens:
		if question.qsentence.parse.tokens[i].pos == "NNP" and question.qsentence.parse.tokens[i].token != None:
			nnp1 = str(question.qsentence.parse.tokens[i].token)
			break
	if nnp1 != None:	
		for i, answer in enumerate(question.answers):
			if answer.parse.tokens[1].pos == "PRP":
				a1 = str(answer)
				a2 = a1.replace(answer.parse.tokens[1].token, nnp1, 1)
				a3 = a2.replace(" ", "", 1)
				qalist[i][0] = str(a3)
	return qalist
