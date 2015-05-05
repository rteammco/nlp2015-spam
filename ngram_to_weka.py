# docs

# python ngram_to_weka.py trec07p Data/NGramTest/lower_chars 60001 60003 Models lower_chars out.txt 3 5


import argparse
import subprocess


JAVA_CP  = 'berkeleylm-1.1.6/src'
LM_CLASS = 'edu.berkeley.nlp.lm.io.ComputeLogProbabilityOfTextStream'
JAVA_CMD = 'java -ea -mx1000m -server -cp ' + JAVA_CP + ' ' + LM_CLASS


def run_bash_cmd(command):
    """Executes a bash command and returns its output as a string."""
    p = subprocess.Popen(command.split(), \
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if len(out.strip()) == 0:
        print "Output failed on command:"
        print command
        print "Error was: " + err
        exit(0)
    return out


def extract_probability(model_output):
    """Returns the probability extracted from the Berkley LM output text."""
    return model_output.strip().split()[-1]


def ngram_to_weka(args):
    """
    Evaluates each input message on both the spam and ham N-Gram models for
    each value of N provided. Returns a list of tuples, where each tuple
    contains the message number, the message label (spam or ham), and a list
    of inner tuples for each N-Gram. Each inner tuple contains the value of N
    for that particular model, followed by the ham and spam log probabilities,
    respectively.
    e.g.
    [(60001, 'ham', [(3, '-2341.23', '-3245.32'), (5, '-3241.33', '-3421.32']),
     (60002, 'ham', [(3, '-5241.64', '-2512.42'), (5, '-1325.78', '3513.23')])]
    """
    label_file = open(args.data_dir + 'full/index', 'r')
    labels = label_file.readlines()
    label_file.close()
    labels = [label.split()[0] for label in labels]
    outputs = []
    model_bin_ham = args.model_type + '_ham.binary'
    model_bin_spam = args.model_type + '_spam.binary'
    for num in range(args.range_start, args.range_end+1):
        label = labels[num-1]
        msg_file = args.in_dir + 'message_' + str(num)
        probs = []
        for n_val in args.N_vals:
            n_prefix = 'N_' + str(n_val) + '_'
            model_bin_ham_N = args.model_dir + n_prefix + model_bin_ham
            model_bin_spam_N = args.model_dir + n_prefix + model_bin_spam
            ham_output = run_bash_cmd(JAVA_CMD + ' ' + model_bin_ham_N + ' ' + msg_file)
            ham_prob = extract_probability(ham_output)
            spam_output = run_bash_cmd(JAVA_CMD + ' ' + model_bin_spam_N + ' ' + msg_file)
            spam_prob = extract_probability(spam_output)
            probs.append((n_val, ham_prob, spam_prob))
        outputs.append((num, label, probs))
    return outputs


# Process args and run the evaluation code.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir', \
                        help="Trec 2007 corpus directory.")
    parser.add_argument('in_dir', \
                        help="Directory of the input N-Gram files.")
    parser.add_argument('range_start', type=int, \
                        help="First file in the data batch.")
    parser.add_argument('range_end', type=int, \
                        help="Last file in the data batch.")
    parser.add_argument('model_dir', \
                        help="Directory of the binary model files.")
    parser.add_argument('model_type', \
                        help="Which model to use (e.g. chars_upper).")
    parser.add_argument('outfile', \
                        help="Output .arff file or N-Gram file/directory.")
    parser.add_argument('N_vals', type=int, nargs='+',
                        help='A list of N values (N-Gram model types).')
    args = parser.parse_args()
    if not args.data_dir.endswith('/'):
        args.data_dir += '/'
    if not args.in_dir.endswith('/'):
        args.in_dir += '/'
    if not args.model_dir.endswith('/'):
        args.model_dir += '/'
    outputs = ngram_to_weka(args)
    print "Message # | label | ham prob | spam prob"
    for output in outputs:
        print output
