# Given N-Gram models and data, this script will run the Berkeley LM classifier
# on the existing N-Gram model binaries and evaluate each message in the Data
# directory provided. The output will be stored in a .arff training file for
# the Weka classifier to train on.
#
# Some example use cases:
#  $ python ngram_to_weka.py trec07p Data/NGramTest 60001 60003 Models lower_chars out.txt 3 5
#  $ python ngram_to_weka.py trec07p Data/NGramTest 60001 60003 Models lower_chars/lower_words out.txt 3 4 5
#  $ python ngram_to_weka.py trec07p Data/NGramTest 60001 60003 Models all out.txt 3
#
# Or, using the config file (see documentation in that file):
#  $ python ngram_to_weka.py trec07p Data/NGramTest 60001 60003 Models config out.txt


import argparse
import subprocess


JAVA_EXE = '/u/teammco/Documents/Java/jdk1.8.0_40/bin/java'
JAVA_CP  = 'berkeleylm-1.1.6/src'
LM_CLASS = 'edu.berkeley.nlp.lm.io.ComputeLogProbabilityOfTextStream'
JAVA_CMD = JAVA_EXE + ' -ea -mx1000m -server -cp ' + JAVA_CP + ' ' + LM_CLASS


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


def join_outputs(outputs, new_outputs):
    """Adds all features of the new_outputs to the existing outputs list."""
    if len(outputs) == 0:
        return new_outputs
    else:
        assert(len(outputs) == len(new_outputs))
        for i in range(len(outputs)):
            for feature in new_outputs[i][2]:
                outputs[i][2].append(feature)
        return outputs


def ngram_to_weka(args, models):
    """
    Evaluates each input message on both the spam and ham N-Gram models for
    each value of N provided. Returns a list of tuples, where each tuple
    contains the message number, the message label (spam or ham), and a list
    of inner tuples for each N-Gram. Each inner tuple contains the value of N
    for that particular model, followed by the ham and spam log probabilities,
    respectively.
    e.g.
    [(60001, 'ham', ['-2341.23', '-3245.32', '-3241.33', '-3421.32']),
     (60002, 'ham', ['-5241.64', '-2512.42', '-1325.78', '-3513.23'])]
    """
    # Read the labels file from the raw data set (ham or spam).
    label_file = open(args.data_dir + 'full/index', 'r')
    labels = label_file.readlines()
    label_file.close()
    labels = [label.split()[0] for label in labels]
    # Process each model separately, with all of its prescribed N values.
    outputs = []
    for model in models:
        print "Evaluating on model: " + str(model)
        cur_outputs = []
        model_type = model[0]
        n_vals = model[1]
        in_dir = args.in_dir + model_type + '/'
        model_bin_ham = model_type + '_ham.binary'
        model_bin_spam = model_type + '_spam.binary'
        # Process every message in the range.
        count = 0
        total = float((args.range_end + 1) - args.range_start)
        one_percent_msgs = int(total / 100)
        for num in range(args.range_start, args.range_end+1):
            count += 1
            if count % one_percent_msgs == 0:
                percent_done = int(100 * (float(count) / total))
                print "    " + str(percent_done) + "% done..."
            label = labels[num-1]
            msg_file = in_dir + 'message_' + str(num)
            probs = []
            # Process for each message all N-values for this model.
            for n_val in n_vals:
                n_prefix = 'N_' + str(n_val) + '_'
                model_bin_ham_N = args.model_dir + n_prefix + model_bin_ham
                model_bin_spam_N = args.model_dir + n_prefix + model_bin_spam
                ham_output = run_bash_cmd(JAVA_CMD + ' ' + model_bin_ham_N + ' ' + msg_file)
                ham_prob = extract_probability(ham_output)
                spam_output = run_bash_cmd(JAVA_CMD + ' ' + model_bin_spam_N + ' ' + msg_file)
                spam_prob = extract_probability(spam_output)
                probs += [ham_prob, spam_prob]
            cur_outputs.append((num, label, probs))
        outputs = join_outputs(outputs, cur_outputs)
    return outputs


def add_feature(outputs, values):
    """Adds the given list of features at the end of each output."""
    # TODO - untested
    assert(len(outputs) == len(values))
    for val in values:
        outputs[2].append(val)


def write_arff_file(models, outputs, outfname):
    """
    Writes the .arff weka file using the given output values. The outputs
    should be formatted the same way as the return format of the
    "ngram_to_weka" function. Additional values may be inserted as tuples
    using the "add_feature" function. Added features should not be regular
    strings, and if they are, they must be *in quotes* and *escaped*.
    """
    outfile = open(outfname, 'w')
    outfile.write("% ARFF generated by Python N-Gram to Weka script.\n\n")
    outfile.write("@RELATION ngram\n\n")
    for model in models:
        model_type = model[0]
        n_vals = model[1]
        for n_val in n_vals:
            for msg_class in ['ham', 'spam']:
                attr = 'N_' + str(n_val) + '_' + model_type + '_' + msg_class
                outfile.write("@ATTRIBUTE " + attr + " NUMERIC\n")
    outfile.write("@ATTRIBUTE spam_or_ham_class {spam,ham}\n\n")
    outfile.write("@DATA\n")
    for output in outputs:
        msg_class = output[1]
        features = output[2]
        for feature in features:
            outfile.write(feature + ' ')
        outfile.write(msg_class + '\n')
    outfile.close()


def get_models_from_config(args):
    """
    Sets up model types (which models and N values to use) according to the
    config file 'ngram_to_weka.config'.
    """
    config_file = open('ngram_to_weka.config', 'r')
    lines = config_file.readlines()
    config_file.close()
    models = []
    for line in lines:
        line = line.strip()
        if len(line) == 0 or line[0] == '#':
            continue
        model_type, n_vals = line.split(':')
        n_vals = n_vals.split(',')
        n_vals = map(str.strip, n_vals)
        if len(n_vals) == 0:
            print "Error: malformed config file:"
            print "  Each model must have at least one N value."
            exit(0)
        models.append((model_type, n_vals))
    return models


def get_models_from_args(args):
    """
    Sets up model types (which models and N values to use) according to the
    args passed in to the program.
    """
    if args.model_type == 'all':
        args.model_type = 'lower_chars/lower_words/upper_chars/upper_words'
    args.model_type = args.model_type.split('/')
    models = []
    for model_type in args.model_type:
        n_vals = []
        for N in args.N_vals:
            n_vals.append(N)
        models.append((model_type, n_vals))
    return models


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
                        help="Which model to use (e.g. chars_upper). " + \
                             "Optionally, 'all' for all models, or 'config' " + \
                             "to load config file for more advanced options.")
    parser.add_argument('outfile', \
                        help="Output .arff file or N-Gram file/directory.")
    parser.add_argument('N_vals', type=int, nargs='*',
                        help="A list of N values (N-Gram model types). Need " + \
                             "at least one unless using the 'config' option.")
    args = parser.parse_args()
    if args.model_type == 'config':
        models = get_models_from_config(args)
    else:
        models = get_models_from_args(args)
        if len(args.N_vals) < 1:
            print "Please provide at least one N value:\n"
            parser.print_help()
            exit(0)
    if not args.data_dir.endswith('/'):
        args.data_dir += '/'
    if not args.in_dir.endswith('/'):
        args.in_dir += '/'
    if not args.model_dir.endswith('/'):
        args.model_dir += '/'
    outputs = ngram_to_weka(args, models)
    #print models
    #for output in outputs:
    #    print output
    write_arff_file(models, outputs, args.outfile)
