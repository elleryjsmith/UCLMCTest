from classes import storyparser
from features.bow import bow
import sys
import copy


def how_many(bow_result):
    return -bow_result[1]


def bow_q_select(story, question_n, sentence_n):
    question = story.questions[question_n].qsentence.parse.lemma
    sentence = story.sentences[sentence_n].parse.lemma
    return bow(question, sentence, bow_filter=None)


def bow_qa_select(story, question_n, sentence_n):
    question = story.questions[question_n].qsentence.parse.lemma
    answers = [
        l
        for a in story.questions[question_n].answers
        for l in a.parse.lemma
    ]
    sentence = story.sentences[sentence_n].parse.lemma
    return bow(question + answers, sentence, bow_filter=None)


def select_sentences(story, question_n, score_f=bow_q_select, limit=2):
    selected = [
        (s, len(score_f(story, question_n, sentence_n)))
        for sentence_n, s in enumerate(story.sentences)
    ]
    selected = sorted(selected, key=how_many)
    return [s[0] for s in selected[:limit]]


def filtered_story(story, question_n, score_f=bow_q_select, limit=2):
    new_story = copy.deepcopy(story)
    new_story.sentences = select_sentences(
        story,
        question_n,
        score_f=score_f,
        limit=limit
    )
    new_story.questions = [story.questions[question_n]]
    return new_story


if __name__ == "__main__":
    if len(sys.argv) == 2:
        testset = sys.argv[1]
        stories = list(storyparser(testset))
        story = filtered_story(stories[0], 3, score_f=bow_qa_select)
        print story

    else:
        sys.stderr.write(
            "Usage: python %s <dataset> (e.g. mc160.dev)\n" % (sys.argv[0]))
