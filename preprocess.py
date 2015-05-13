# Python script to convert the raw email data into .arff format for Weka,
# or outputs N-gram processing files from the raw email data.

import sys
import argparse
import re
import email
from collections import OrderedDict


# Fill this list using load_stopwords() function.
STOPWORDS = []

# Regex to match any number (int or float) within a string.
FLOAT_REGEX = r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?'

# Range of allowable ASCII characters (rest are ignored).
ASCII_MIN = 32
ASCII_MAX = 126

# Alls symbols to be ignored by the filters.
SYMBOLS = [
    '~', '`', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+',
    '=', '{', '}', '[', ']', '\\', '|', ':', ';', '"', '\'', ',', '.', '?', '/'
]


def filter_words(words):
    """
    Removes all unwanted symbols from each word, and splits words around
    unwanted delimiters. Also removes digits and any excessive white space.
    After all filtering is done, stopwords are also removed (assuming
    stopwords list is filled). The result is returned as a list of words.
    NOTE: The words are NOT converted into lowercase in the final output.
    This is a word-by-word preprocessing step.
    """
    filtered = []
    for word in words:
        # Replace digits with arbitrary symbol, and split around it later
        word = re.sub(FLOAT_REGEX, SYMBOLS[0], word)
        split = False
        for symbol in SYMBOLS:
            if symbol in word:
                parts = word.split(symbol)
                words.extend(parts)
                split = True
                break
        if (not split) and (len(word) > 0) and (word.lower() not in STOPWORDS):
            filtered.append(word)
    return filtered


def process_text(text):
    """
    Processes a single string of text and returns an untagged version of it.
    That is, removes any HTML tags, and any content contained inside the tags,
    and returns the string as raw words. Non-ascii characters will be replaced
    with blank spaces.
    This is a character-by-character preprocessing step that also calls the
    word-for-word preprocessing step after it finishes.
    Returns a single space-delimited string of preprocessed words.
    """
    # remove HTML tags and non-ascii characters:
    words = text.split()
    intag = False
    raw_words = []
    num_urls = 0
    for word in words:
        if 'href' in word:
            num_urls += 1
        untagged = ''
        for ch in word:
            if ch == '<':
                intag = True
            elif ch == '>':
                intag = False
            elif (not intag):
                if (ASCII_MIN <= ord(ch) <= ASCII_MAX):
                    untagged += ch
                else:
                    untagged += ' '
        if len(untagged) > 0:
            raw_words.append(untagged)
    # Set up some meta data features.
    meta_data = OrderedDict()
    # TODO - count number of sentences (feature)?
    meta_data['Num-URLs'] = num_urls
    meta_data['Num-Words'] = len(raw_words)
    meta_data['Num-Chars'] = len(''.join(raw_words))
    # remove stopwords, numbers, and symbols:
    raw_words = filter_words(raw_words)
    meta_data['Num-Words-Filtered'] = len(raw_words)
    meta_data['Num-Chars-Filtered'] = len(''.join(raw_words))
    raw_text = ' '.join(raw_words)
    return raw_text, meta_data


def process_multipart(part):
    """
    Recursively processes a part of the message body content. If the current
    part is a string or text, returns the string. If it is a chunk of another
    multipart segment, it will recursively return all of the containing
    email body text strings (concatenated into a single string).
    """
    if type(part) is str:
        return part, 0
    maintype = part.get_content_maintype()
    if maintype == 'text':
        return part.get_payload(), 0
    elif maintype == 'multipart':
        text = ''
        img_count = 0
        for sub_part in part.get_payload():
            sub_text, sub_img_count = process_multipart(sub_part)
            text += ' ' + sub_text
            img_count += sub_img_count
        return text, img_count
    elif maintype == 'image':
        return '', 1
    else:
        return '', 0


def process_message(mime_file):
    """
    Separately processes the email stored in the provided MIME file, and
    returns the clean (processed) body content, as well as a dictionary
    containing all of the extracted email meta data.
    """
    message = email.message_from_file(mime_file)
    body, num_images = process_multipart(message)
    print body
    #body = ''
    #num_images = 0
    #for part in message.walk():
    #    text, img_count = process_multipart(part)
    #    body += text
    #    num_images += img_count
    body, meta_data = process_text(body)
    print body
    # Add custom features to meta data.
    meta_data['Num-Images'] = num_images
    # Add other extracted features to meta data.
    raw_meta_data = dict((key, val) for key, val in message.items())
    #meta_data['Content-Length'] = raw_meta_data['Content-Length']
    #meta_data['Num-Lines'] = raw_meta_data['Lines']
    #meta_data['Content-Type'] = raw_meta_data['Content-Type']
    if 'Subject' in raw_meta_data.keys():
        subject = raw_meta_data['Subject']
        subject = ' '.join(filter_words(subject.split()))
        meta_data['Subject'] = subject
    else:
        meta_data['Subject'] = ''
    return body, meta_data


def output_length_file(messages, args):
    """
    Writes a file that contains the total message lengths for each email.
    The file will have to space-separated numbers per line: the first is
    the number of words in the message, and the second number is the number
    of characters in that message.
    The messages will not be numbered. It is recommended to only run this on
    the entire data set at once.
    Messages are a triplet: (body, meta_data, label)
    """
    outfile = open(args.outfile, 'w')
    # TODO - modify this to use the meta_data directly.
    for triplet in messages:
        message = triplet[0]
        list_of_words = message.split()
        num_words = len(list_of_words)
        num_chars = len(''.join(list_of_words))
        outfile.write(str(num_words) + " " + str(num_chars) + "\n")
    outfile.close()


def output_arff_file(messages, args):
    """
    Writes the message and label pairs to an ARFF file.
    Messages are a triplet: (body, meta_data, label)
    """
    outfile = open(args.outfile, 'w')
    outfile.write("% ARFF generated by Python preprocessing script.\n\n")
    outfile.write("@RELATION email\n\n")
    outfile.write("@ATTRIBUTE body STRING\n")
    if args.use_meta and len(messages) > 0:
        example_meta_data = messages[0][1]
        for key in example_meta_data.keys():
            key = str(key).replace('-', '_').lower()
            if key != 'subject':
                outfile.write("@ATTRIBUTE attribute_" + key + " NUMERIC\n")
        # TODO - make sure subject is handled with Bag-of-Words
        outfile.write("@ATTRIBUTE attribute_subject STRING\n")
    outfile.write("@ATTRIBUTE spam_or_ham_class {spam,ham}\n\n")
    outfile.write("@DATA\n")
    for triplet in messages:
        message = triplet[0]
        outfile.write("\"" + message + "\", ")
        if args.use_meta:
            meta_data = triplet[1]
            for key in meta_data:
                if str(key) != 'Subject':
                    outfile.write(str(meta_data[key]) + ", ")
            subject = '"' + meta_data['Subject'].replace('"', '\\"') + '"'
            outfile.write(subject + ", ")
        label = triplet[2]
        outfile.write(label + "\n")
    outfile.close()


def output_ngram_files(messages, args):
    """
    For both training and testing data, the output will be a LIST of files
    (output and named in order numerically by the range values) for each
    message, and there will not be a label on those files. However, for
    training data only (i.e. if "args.ngram_test" is False), the output will
    also generate two additional files: one for ham emails and another for
    spam messages, depending on their paired labels.
    If parameter "args.ngram_chars" is True, the words are also going to be
    split up into space-delimited characters before being written out to the
    output file. Similarly, if "args.ngram_lower" is True, every word or
    character will be converted to lowercase first.
    Messages are a triplet: (body, meta_data, label)
    """
    # TODO - this needs to be rewritten: we're doing the work twice now
    all_messages = []
    ham_messages = []
    spam_messages = []
    # If this is for test data, put all messages into the ham pile. The spam
    # list will be empty, so nothing will happen to it.
    for triplet in messages:
        message = triplet[0]
        label = triplet[2]
        all_messages.append(message)
        if not args.ngram_test:
            if label == 'ham':
                ham_messages.append(message)
            else:
                spam_messages.append(message)
    if args.ngram_lower:
        all_messages = map(str.lower, all_messages)
        ham_messages = map(str.lower, ham_messages)
        spam_messages = map(str.lower, spam_messages)
    if args.ngram_chars:
        categories = []
        # Repeat for both categories: spam and ham messages.
        for category in [all_messages, ham_messages, spam_messages]:
            messages_as_list_of_characters = map(list, category)
            category = []
            # Convert each message (a list of characters) to a space-delimited
            # string of characters, dropping any extra spaces.
            for message in messages_as_list_of_characters:
                category.append(' '.join([ch for ch in message if ch != ' ']))
            categories.append(category)
        all_messages = categories[0]
        ham_messages = categories[1]
        spam_messages = categories[2]
    counter = args.range_start
    for message in all_messages:
        slash = '/'
        if args.outfile[-1] == '/':
            slash = ''
        outfname = args.outfile + slash + 'message_' + str(counter)
        outfile = open(outfname, 'w')
        outfile.write(message)
        outfile.close()
        counter += 1
    # For training, write two files, one for all hams and one for all all spams:
    if not args.ngram_test:
        for category in [('ham', ham_messages), ('spam', spam_messages)]:
            category_name = category[0]
            category_messages = category[1]
            fpath = args.outfile.split('/')
            fpath[-1] = fpath[-1] + '_' + category_name
            outfname = '/'.join(fpath)
            outfile = open(outfname, 'w')
            outfile.write("\n") # a newline must be on top for BerkleyLM tool
            for message in category_messages:
                outfile.write(message + "\n")
            outfile.close()


def preprocess(args):
    """
    Converts the data from each file in the given range into a single string
    of words extracted out of the message body. The words are pre-filtered
    to remove symbols, numbers, and other filler content.
    The processed data is compiled into a single ARFF file, which can then
    be further preprocessed and converted into a bag-of-words format using
    Weka's filter tools.
    """
    label_file = open(args.data_dir + '/full/index', 'r')
    labels = label_file.readlines()
    label_file.close()
    data_dir = args.data_dir + '/data'
    messages = []
    for num in range(args.range_start, args.range_end+1):
        label = labels[num-1].split()[0]
        fname = data_dir + '/inmail.' + str(num)
        mime_file = open(fname, 'r')
        body, meta_data = process_message(mime_file)
        mime_file.close()
        messages.append((body, meta_data, label))
        #print "================================ Message " + str(num)
    # Handle N-Gram output option.
    if args.to_ngrams:
        if args.ngram_all:
            options = [ # name, lowercase?, characters?
                ('upper_words', False, False),
                ('lower_words', True,  False),
                ('upper_chars', False, True),
                ('lower_chars', True,  True),
            ]
            outdir = args.outfile
            for opt in options:
                args.outfile = outdir + '/' + opt[0]
                args.ngram_lower = opt[1]
                args.ngram_chars = opt[2]
                print opt
                output_ngram_files(messages, args)
        else:
            output_ngram_files(messages, args)
    # Handle length file output option.
    elif args.to_lengths:
        output_length_file(messages, args)
    # Otherwise output regular bag of words .arff files.
    else:
        output_arff_file(messages, args)


def load_stopwords(fname):
    """
    Reads the file of the given filename and saves all the stopwords which
    will be used in the filtering process to remove them from the text.
    All stopwords will be converted to lowercase if they are not already.
    """
    stopwords_file = open(fname, 'r')
    for line in stopwords_file:
        stopword = line.strip()
        if (len(stopword) > 0) and (stopword[0] != '#'):
            STOPWORDS.append(stopword.lower())
    stopwords_file.close()


# Process args and run the preprocessing code.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir', \
                        help="Trec 2007 corpus directory.")
    parser.add_argument('range_start', type=int, \
                        help="First file in the data batch.")
    parser.add_argument('range_end', type=int, \
                        help="Last file in the data batch.")
    parser.add_argument('outfile', \
                        help="Output .arff file or N-Gram file/directory.")
    parser.add_argument('-stopwords', '--swfile', required=False, \
                        help="File of line-separated stopwords.")
    parser.add_argument('--ngrams', dest='to_ngrams', action='store_true', \
                        help="Set to true to output N-Gram format instead.")
    parser.add_argument('--ngram-chars', dest='ngram_chars', action='store_true', \
                        help="Use N-Gram characters instead of words.")
    parser.add_argument('--ngram-lower', dest='ngram_lower', action='store_true', \
                        help="Use only lowercase N-Grams.")
    parser.add_argument('--ngram-all', dest='ngram_all', action='store_true', \
                        help="Generates all 4 combinations of NGram options.")
    parser.add_argument('--ngram-test', dest='ngram_test', action='store_true', \
                        help="NGram output is formatted for test data instead.")
    parser.add_argument('--lengths', dest='to_lengths', action='store_true', \
                        help="Set to true to output length file instead.")
    parser.add_argument('--use-meta', dest='use_meta', action='store_true', \
                        help="Set to true to include meta data in .arff file.")
    args = parser.parse_args()
    # Make sure only ngrams or lengths are specified, not both.
    if args.to_lengths and args.to_ngrams:
        print "ERROR: Please use --ngrams OR --lengths, but not both."
        exit(0)
    if (not args.to_ngrams) and (args.swfile):
        load_stopwords(args.swfile)
    preprocess(args)
