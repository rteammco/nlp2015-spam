import sys


def process_input(in_lines, predicted_class):
    """
    Extract the accuracy/precision/recall from the Weka output.
    Prints the original lines of the output, but also returns the
    a/p/r values.
    """
    num_correctly_predicted = 0
    num_predicted = 0
    num_actual = 0
    num_total = 0
    num_correct = 0
    for line in in_lines:
        if len(line) == 0 or line.startswith('='):
            continue
        parts = line.split()
        if not parts[0].isdigit():
            continue
        actual = parts[1].split(':')[1]
        predicted = parts[2].split(':')[1]
        if actual == predicted:
            num_correct += 1
        if actual == predicted and predicted == predicted_class:
            num_correctly_predicted += 1
        if predicted == predicted_class:
            num_predicted += 1
        if actual == predicted_class:
            num_actual += 1
        num_total += 1
    accuracy = float(num_correct) / float(num_total)
    precision = float(num_correctly_predicted) / float(num_predicted)
    recall = float(num_correctly_predicted) / float(num_actual)
    return accuracy, precision, recall


if __name__ == '__main__':
    in_lines = []
    outputs = []
    for line in sys.stdin:
        line = line.strip()
        outputs.append(line)
        in_lines.append(line)
    accuracy, precision, recall = process_input(in_lines, 'spam')
    outputs.append("\n\n")
    outputs.append("Accuracy / Precision / Recall:")
    outputs.append(str(accuracy) + " / " + str(precision) + " / " + str(recall))
    outfile = open('out.txt', 'w')
    for out in outputs:
        outfile.write(out + "\n")
