import sys
import os
sys.path.append(os.path.abspath('../../'))

from UCLMCTest.features import bow
from UCLMCTest.classes import storyparser, answers, Question

testset = "mc160.dev"
stories = list(storyparser(testset))
solutions = list(answers(testset))
