
from srilm import *


def instantiateLM():
	languagemodel = initLM(3)
	readLM(languagemodel, "wikimodel.lm")
	return languagemodel

def getSentenceProbability(lmodel, sentence):
	return getSentenceProb(lmodel, sentence, len(sentence.split()))


def lmfilter(lmodel, answers):
	highestanswer = None
	highestscore = None
	for a in answers:
		score = getSentenceProbability(lmodel, a)
		if score > highestscore:
			highestscore = score
			highestanswer = a
	return highestanswer
