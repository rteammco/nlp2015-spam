from nltk.probability import LidstoneProbDist
from nltk.probability import SimpleGoodTuringProbDist
from nltk.model import NgramModel


def train_model(data, N):
    """
    Trains an N-gram model (N is a parameter) on the given data (list of raw
    email message strings). The model is then returned.
    The provided training data should consist of a type of message (i.e. only
    ham messages or only spam messages). It should be a list of full messages.
    """
    # convert data into a single list of words
    data = map(str.split, data)
    data = [item for sublist in data for item in sublist]
    estimator = lambda fdist, bins: LidstoneProbDist(fdist, 1)
    model = NgramModel(N, data, estimator=estimator)
    return model


s1 = 'this is a test sentence and it is very good without a double the test sentence is good'
s2 = 'this is another sentence and I would like to also test it please'

data = [s1, s2]
model = train_model(data, 3)
print model.prob('test', ['also'])
print model.prob('test', ['a'])
print model.prob('thinkwould', ['would'])
exit(0)



estimator = lambda fdist, bins: SimpleGoodTuringProbDist(fdist, 0.1)
lm = NgramModel(2, s1, estimator=estimator)

print lm.prob("good", ["very"])
print lm.prob("good", ["not"])
print lm.prob("good", ["unknown_term"])
