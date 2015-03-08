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