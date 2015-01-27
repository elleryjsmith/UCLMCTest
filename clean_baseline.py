from storyparser import storyparser, Question, similarity, answers

def score(story, question_n, answer_n):
    question = story.questions[question_n]
    answer = question.answers[answer_n]
    qa_pair = question.qsentence.parse.lemma + answer.parse.lemma
    similarities = [similarity(qa_pair, s.parse.lemma) for s in story.sentences]
    return (max([len(s) for s in similarities]), similarities)

def baseline(stories, solutions, mode=None, debug=False):
    scored, total = 0, 0
    for story, solution in zip(stories, solutions):
        for q, question in enumerate(story.questions):
            if question.mode == mode:
                continue
            max_index, max_score = -1, (-1, None)
            for a, _ in enumerate(question.answers):
                current_score = score(story, q, a)
                if current_score[0] > max_score[0]:
                    max_index = a
                    max_score = current_score

            best_answer = chr(max_index + 0x41)
            correct = best_answer == solution[q]
            if correct:
                scored += 1

            total += 1
            if (debug):
                print "Correct:%i\nQuestion matched:\n%s\nWords count: %i\nWords matched:\n%s\n\n" % (correct, question, current_score[0], current_score[1])

    return {
        "total": total,
        "scored": scored,
        "accuracy": (scored * 1.0 / total) * 100
    }

testset = "mc160.dev"
parserfile = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
stories = storyparser(testset)
solutions = answers(testset)

print baseline(stories, solutions, mode=Question.MULTIPLE, debug=False)