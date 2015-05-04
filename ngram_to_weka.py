

JAVA_CP = 'berkleylm-1.1.6/src'
LM_CLASS = 'edu.berkeley.nlp.lm.io.ComputeLogProbabilityOfTextStream'
JAVA_CMD = 'java -ea -mx1000m -server -cp ' + JAVA_CP + ' ' + LM_CLASS


def bash_cmd(command):
    print command
    return command


def ngram_to_weka(args):
    """
    """
    ###########
    model_bin = 'Models/modelfile.binary'

    x = """cat Data/NGramTest/upper_chars/message_60010 | java -ea -mx1000m -server -cp berkeleylm-1.1.6/src edu.berkeley.nlp.lm.io.ComputeLogProbabilityOfTextStream Models/N_3_upper_chars_ham.binary"""

    trec_file = None # TODO: trec07p/all/index
    # TODO - need one message per file here, fail fail
    train_file = open('Data/NGramTrain/train_', 'r')
    for message in train_file:
        message = message.strip()
        if len(message) == 0:
            continue
        output = bash_cmd('"' + message + '" | ' + JAVA_CMD + ' ' + model_bin)
        break


if __name__ == '__main__':
    print JAVA_CMD
    #ngram_to_weka(0)
