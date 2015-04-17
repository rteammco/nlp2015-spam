# Python script to convert the raw email data into .arff format for Weka.

import sys


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
        print data_dir + 'inmail.' + str(num)
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
