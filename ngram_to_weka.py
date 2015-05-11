# Given N-Gram models and data, this script will run the Berkeley LM classifier
# on the existing N-Gram model binaries and evaluate each message in the Data
# directory provided. The output will be stored in a .arff training file for
# the Weka classifier to train on.
#
# Some example use cases:
#  $ python ngram_to_weka.py trec07p Models/Evaluations 60001 60003 lower_chars out.txt 3 5
#  $ python ngram_to_weka.py trec07p Models/Evaluations 60001 60003 lower_chars/lower_words out.txt 3 4 5
#  $ python ngram_to_weka.py trec07p Models/Evaluations 60001 60003 all out.txt 3
#
# Or, using the config file (see documentation in that file):
#  $ python ngram_to_weka.py trec07p Models/Evaluations 60001 60003 Models config out.txt
#
# Actual run commands on 81/9/10 split (test and train .ARFFs):
#  $ python ngram_to_weka.py trec07p Models/Evaluations 61090 67877 config Data/train_ngram_log.arff --offset 61090 --length-file Data/lengths.txt
#  $ python ngram_to_weka.py trec07p Models/Evaluations 67878 75419 config Data/test_ngram_log.arff --offset 61091 --length-file Data/lengths.txt
#
# And with real probabilities instead of log probs:
#  $ python ngram_to_weka.py trec07p Models/Evaluations 61090 67877 config Data/train_ngram.arff --offset 61090 --length-file Data/lengths.txt --real-probs
#  $ python ngram_to_weka.py trec07p Models/Evaluations 67878 75419 config Data/test_ngram.arff --offset 61091 --length-file Data/lengths.txt --real-probs


import argparse
import math


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
    Returns a list of tuples, where each tuple contains the message number,
    the message label (spam or ham), and a list of inner tuples for each
    N-Gram. Each inner tuple contains the value of N for that particular
    model, followed by the ham and spam log probabilities, respectively.
    e.g.
    [(60001, 'ham', ['-2341.23', '-3245.32', '-3241.33', '-3421.32']),
     (60002, 'ham', ['-5241.64', '-2512.42', '-1325.78', '-3513.23'])]
    Uses existing evaluation files to get the actual log probabilities.
    """
    # Read the labels file from the raw data set (ham or spam).
    label_file = open(args.data_dir + 'full/index', 'r')
    labels = label_file.readlines()
    label_file.close()
    labels = [label.split()[0] for label in labels]
    # If a length file is provided, read those values in as well as a list
    # of tuples: first element is number of words, the second is chars.
    lengths = None
    if args.length_file:
        len_file = open(args.length_file, 'r')
        lengths = len_file.readlines()
        len_file.close()
        lengths = [tuple(map(int, lens.split())) for lens in lengths]
    # Process each model separately, with all of its requested N values.
    outputs = []
    for model in models:
        print "Evaluating on model: " + str(model)
        model_type = model[0]
        char_model = ('char' in model_type)
        n_vals = model[1]
        # Get the values for each message all N-values for this model.
        value_sets = []
        for n_val in n_vals:
            model_name = 'N_' + str(n_val) + '_' + model_type
            ham_eval_fpath = args.in_dir + model_name + '_ham'
            spam_eval_fpath = args.in_dir + model_name + '_spam'
            ham_eval_file = open(ham_eval_fpath, 'r')
            ham_vals = ham_eval_file.readlines()
            ham_eval_file.close()
            spam_eval_file = open(spam_eval_fpath, 'r')
            spam_vals = spam_eval_file.readlines()
            spam_eval_file.close()
            value_sets.append((ham_vals, spam_vals))
        # Process every message in the range.
        cur_outputs = []
        for num in range(args.range_start, args.range_end+1):
            file_index = num - args.offset - 1
            label = labels[num-1]
            length = None
            if lengths:
                length = lengths[num-1]
                length = length[1] if char_model else length[0]
            probs = []
            for pair in value_sets:
                ham_prob = eval(pair[0][file_index].strip())
                spam_prob = eval(pair[1][file_index].strip())
                if length and length > 0:
                    ham_prob /= length
                    spam_prob /= length
                if args.real_probs:
                    ham_prob = math.exp(ham_prob)
                    spam_prob = math.exp(spam_prob)
                probs += [ham_prob, spam_prob]
            cur_outputs.append((num, label, probs))
        outputs = join_outputs(outputs, cur_outputs)
    return outputs


def add_BoW_features(outputs, bow_file):
    """
    Adds the text feature from a bulk .ARFF file to the existing features
    from the N-Grams.
    """
    infile = open(bow_file, 'r')
    in_lines = infile.readlines()
    infile.close()
    data_section = False
    index = 0
    for line in in_lines:
        line = line.strip()
        if len(line) == 0:
            continue
        elif data_section:
            data = line.split(",")
            text = data[0]
            outputs[index][2].insert(0, text)
            index += 1
        elif line.lower().find('@data') == 0:
            data_section = True


def copy_attributes(in_fname, outfile):
    """
    Copies the attributes from the first .arff file (provided as a file name)
    into the second file (provided as a writeable file handle).
    """
    infile = open(in_fname, 'r')
    in_lines = infile.readlines()
    infile.close()
    for line in in_lines:
        line = line.strip()
        lwr_line = line.lower()
        if lwr_line.find('@attribute') == 0 and \
           lwr_line.find('spam_or_ham_class') < 0:
            outfile.write(line + "\n")


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
    outfile.write("@RELATION ngrams\n\n")
    # Copy any and all bag-of-words attributes.
    if args.bow_file:
        copy_attributes(args.bow_file, outfile)
    # Write all the N-Gram attributes.
    for model in models:
        model_type = model[0]
        n_vals = model[1]
        for n_val in n_vals:
            for msg_class in ['ham', 'spam']:
                attr = 'N_' + str(n_val) + '_' + model_type + '_' + msg_class
                outfile.write("@ATTRIBUTE " + attr + " NUMERIC\n")
    outfile.write("@ATTRIBUTE spam_or_ham_class {spam,ham}\n\n")
    outfile.write("@DATA\n")
    # Write all the data.
    for output in outputs:
        msg_class = output[1]
        features = output[2]
        for feature in features:
            outfile.write(str(feature) + ' ')
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
                        help="Directory of the evaluated N-Grams.")
    parser.add_argument('range_start', type=int, \
                        help="First file in the data batch.")
    parser.add_argument('range_end', type=int, \
                        help="Last file in the data batch.")
    parser.add_argument('model_type', \
                        help="Which model to use (e.g. chars_upper). " + \
                             "Optionally, 'all' for all models, or 'config' " + \
                             "to load config file for more advanced options.")
    parser.add_argument('outfile', \
                        help="Output .arff file or N-Gram file/directory.")
    parser.add_argument('N_vals', type=int, nargs='*',
                        help="A list of N values (N-Gram model types). Need " + \
                             "at least one unless using the 'config' option.")
    parser.add_argument('--offset', dest='offset', type=int,
                        help="Offset accounting for N-Gram training data (default 0).")
    parser.add_argument('--length-file', dest='length_file',
                        help="A specially formatted length file containing the " + \
                             "lengths of all messages for both words and characters. " + \
                             "If set, length will be taken into account.")
    parser.add_argument('--BoW-file', dest='bow_file',
                        help="An additional .ARFF file containing bag of words " + \
                             "features to add to the new .ARFF outfile.")
    parser.add_argument('--real-probs', dest='real_probs', action='store_true', \
                        help="Convert Log probabilities to real probabilities.")
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
    if not args.offset:
        args.offset = 0
    outputs = ngram_to_weka(args, models)
    if args.bow_file:
        add_BoW_features(outputs, args.bow_file)
    write_arff_file(models, outputs, args.outfile)
