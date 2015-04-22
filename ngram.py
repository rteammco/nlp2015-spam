from nltk.probability import LidstoneProbDist
from nltk.model import NgramModel


def train_model(data, N):
    """
    Trains an N-gram model (N is a parameter) on the given data (list of raw
    email message strings). The model is then returned.
    """
    pass


test_sent = 'this is a test sentence and it is very good without a double the test sentence is good'.split()


estimator = lambda fdist, bins: LidstoneProbDist(fdist, 0.9)
lm = NgramModel(2, test_sent, estimator=estimator)

print lm.prob("good", ["very"])
print lm.prob("good", ["not"])
print lm.prob("good", ["unknown_term"])
