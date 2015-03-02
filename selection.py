from classes import storyparser
from features.bow import bow
import sys
import copy


def how_many(bow_result):
    return bow_result[1]


def bow_select(question, sentence):
    return bow(question, sentence, bow_filter=None, skip_none=True)


def select_sentences(story, question_n, score_f=bow_select, limit=2):
    q_lemma = story.questions[question_n].qsentence.parse.lemma
    selected = [
        (s, len(score_f(q_lemma, s.parse.lemma)))
        for s in story.sentences
    ]
    selected = sorted(selected, key=how_many)
    return [s[0] for s in selected[:limit]]


def filtered_story(story, question_n, score_f=bow_select, limit=2):
    new_story = copy.deepcopy(story)
    new_story.sentences = select_sentences(
        story,
        question_n,
        score_f=score_f,
        limit=limit
    )
    return new_story


if __name__ == "__main__":
    if len(sys.argv) == 2:
        testset = sys.argv[1]
        stories = list(storyparser(testset))
        story = filtered_story(stories[0], 0)
        print story

    else:
        sys.stderr.write(
            "Usage: python %s <dataset> (e.g. mc160.dev)\n" % (sys.argv[0]))
