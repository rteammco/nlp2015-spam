# Python script to convert the raw email data into .arff format for Weka.

import sys


def process(message):
    """
    Processes a single message and returns the raw text.
    """
    words = message.split()
    intag = False
    raw_words = []
    for word in words:
        untagged = ''
        for ch in word:
            if ch == '<':
                intag = True
            elif ch == '>':
                intag = False
            elif not intag:
                untagged += ch
        if len(untagged) > 0:
            raw_words.append(untagged)
    raw_text = ' '.join(raw_words)
    print raw_text
    return raw_text


def convert(data_dir, file_range):
    """
    Converts the given data.
    """
    label_file = open(data_dir + '/full/index', 'r')
    labels = label_file.readlines()
    label_file.close()
    data_dir = data_dir + '/data'
    for num in range(file_range[0], file_range[1]+1):
        label = labels[num-1].split()[0]
        fname = data_dir + '/inmail.' + str(num)
        msg_file = open(fname, 'r')
        message = msg_file.read()
        msg_file.close()
        raw_text = process(message)
        #print message
        print labels[num-1].strip() + " (" + label + ")"


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Please provide a directory and file range."
        exit(0)
    data_dir = sys.argv[1]
    range_start = sys.argv[2]
    range_end = sys.argv[3]
    file_range = (int(range_start), int(range_end))
    convert(data_dir, file_range)
