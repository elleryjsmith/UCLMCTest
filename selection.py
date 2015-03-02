from classes import storyparser
import sys
import copy


def how_many(res):
    return -res[1]


def select_sentences(story, question_n, score_f=None, limit=2):
    if not score_f:
        return story.sentences

    selected = [
        (s, len(score_f(story, question_n, sentence_n)))
        for sentence_n, s in enumerate(story.sentences)
    ]
    selected = sorted(selected, key=how_many)
    return [s[0] for s in selected[:limit]]


def filtered_story(story, question_n, score_f=None, limit=2):
    if not score_f:
        return story
    new_story = copy.deepcopy(story)
    new_story.sentences = select_sentences(
        story,
        question_n,
        score_f=score_f,
        limit=limit
    )
    # new_story.questions = [story.questions[question_n]]
    return new_story
