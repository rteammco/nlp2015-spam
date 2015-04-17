# Python script to convert the raw email data into .arff format for Weka.

import sys
import email


def process_text(text):
    """
    Processes a single string of text and returns an untagged version of it.
    That is, removes any HTML tags, and any content contained inside the tags,
    and returns the string as raw words.
    """
    words = text.split()
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
    return raw_text


def process_message(mime_file):
    """
    Separately processes the email stored in the provided MIME file, and
    returns the clean (processed) body content, as well as header data.
    """
    message = email.message_from_file(mime_file)
    maintype = message.get_content_maintype()
    body = ''
    if maintype == 'multipart':
        for part in message.get_payload():
            if part.get_content_maintype() == 'text':
                body += part.get_payload()
    elif maintype == 'text':
        body = message.get_payload()
    body = process_text(body)
    return dict((key, val) for key, val in message.items()), body


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
        mime_file = open(fname, 'r')
        header, body = process_message(mime_file)
        mime_file.close()
        print body
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
