from storyparser import storyparser, Question, similarity, answers


testset = "mc160.dev"


parserfile = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"


#stories = storyparser(testset,parserfile,debug=True)

stories = storyparser(testset)


solutions = answers(testset)


score,total = 0,0


for story in stories:

  solution = solutions.next()
 
  print story


  for n,question in enumerate(story.questions):


    if question.mode == Question.MULTIPLE:

      continue


    print "\n###\n\nQ:%s\n" % (question.qsentence)
    

    questionstrs = []

    for i,answer in enumerate(question.answers):

      questionstrs.append((question.qsentence.parse.lemma + answer.parse.lemma,answer,chr(i + 0x41)))

    
    bestmatch = (None,None,[],-1)


    for qstr,ans,i in questionstrs:


      for sentence in story.sentences:


        sim = similarity(qstr,sentence.parse.lemma)


        if len(sim) > len(bestmatch[2]):

          bestmatch = (sentence,ans,sim,i)


    total += 1

    ansstr = "Matched sentence:%s\n\nA:%s\n\nMatched words: %s\n" % (bestmatch[0],bestmatch[1],bestmatch[2])

    if bestmatch[3] == solution[n]:

      score += 1

      print ansstr + " (Correct)\n"

    else:
      
      print ansstr + " (Incorrect)\n"


print "\n\n########\n\nQuestions answered: %d\nCorrect Answers: %d\nResult: %d%%" % (total,score,(score*1.0/total)*100)

