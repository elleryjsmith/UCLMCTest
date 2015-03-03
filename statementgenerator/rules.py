

def generatewhostatements(qalist, question):
	q1 = str(question.qsentence)
	q2 = q1.replace("Who ", "", 1)
	qf = q2.replace("?", ".", 1)
	for i, answer in enumerate(question.answers):
		a = str(answer)
		concat = a + qf
		qalist[i].append(concat)
	return qalist