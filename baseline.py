from storyparser import storyparser, Question, similarity, answers


testset = "mc160.dev"


parserfile = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"


stories = storyparser(testset,parserfile,debug=True)


score,total = 0,0


for story in stories:

  solutions = answers(testset).next()

  print story


  for n,question in enumerate(story.questions):


    if question.mode == Question.MULTIPLE:

      continue


    print "Q:" + str(question.qsentence)
    

    questionstrs = []

    for i,answer in enumerate(question.answers):

      questionstrs.append((question.qsentence.parse.lemma + answer.parse.lemma,answer,chr(i + 0x41)))

    
    bestmatch = (None,0,-1)


    for qstr,ans,i in questionstrs:


      for sentence in story.sentences:


        sim = similarity(qstr,sentence.parse.lemma)

        if sim > bestmatch[1]:

          bestmatch = (ans,sim,i)


    total += 1

    ansstr = "A:" + str(bestmatch[0])

    if bestmatch[2] == solutions[n]:

      score += 1

      print ansstr + " (Correct)"

    else:
      
      print ansstr + " (Incorrect)"


print "\n\n########\n\nQuestions answered: %d\nCorrect Answers: %d\nResult: %d%%" % (total,score,(score*1.0/total)*100)

