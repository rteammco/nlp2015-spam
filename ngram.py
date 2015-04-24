from collections import defaultdict
import nltk
from nltk.util import ngrams


class NGramModel():
    def __init__(self):
        pass

    def add_sentence(self, sentence):
        pass
    
    def compute_probabilities(self):
        pass

def train_model(data, N, frequencies):
    """
    Trains an N-gram model (N is a parameter) on the given data (list of raw
    email message strings). The model is then returned.
    The provided training data should consist of a type of message (i.e. only
    ham messages or only spam messages). It should be a list of full messages.
    """
    for sentence in data:
        words = ['<S>'] + nltk.word_tokenize(sentence) + ['</S>']
        ngs = ngrams(words, N)
        for ng in ngs:
            frequencies[ng] += 1


s1 = 'this is a test sentence and it is very good without a double the test sentence is good'
s2 = 'this is another sentence and I would like to also test it please'
freq = defaultdict(int)
train_model([s1], 2, freq)
train_model([s2], 2, freq)
print freq
exit(0)



estimator = lambda fdist, bins: SimpleGoodTuringProbDist(fdist, 0.1)
lm = NgramModel(2, s1, estimator=estimator)

print lm.prob("good", ["very"])
print lm.prob("good", ["not"])
print lm.prob("good", ["unknown_term"])
