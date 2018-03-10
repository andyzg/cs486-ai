from collections import defaultdict
from Queue import PriorityQueue as queue
import math


class Doc:

    def __init__(self, id):
        self.id = id
        self.label = None
        self.words = defaultdict(bool)

    def add_word(self, index):
        self.words[index] = True

    def set_label(self, label):
        self.label = label

    def has_word(self, word_id):
        return self.words[word_id]


class Score:

    def __init__(self, score, word_id):
        self.word_id = word_id
        self.score = score

    def __cmp__(self, score):
        if self.score > score.score:
            return -1
        elif self.score < score.score:
            return 1
        return 0


def load_data(filename):
    docs = {}
    last_index = 0
    with open(filename, 'r') as f:
        for line in f.readlines():
            doc_id, word_id = line.rstrip().split('\t')
            doc_id = int(doc_id)
            word_id = int(word_id)

            if doc_id not in docs:
                docs[doc_id] = Doc(doc_id)
                if doc_id - last_index > 1:
                    for i in range(last_index+1, doc_id):
                        docs[i] = Doc(i)

            docs[doc_id].add_word(word_id-1)
            last_index = doc_id

    return docs


def load_test_label(filename):
    label = []
    with open(filename, 'r') as f:
        for i, line in enumerate(f.readlines()):
            label.append(int(line.strip()))
    return label


def load_words(filename):
    words = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            words.append(line.strip())

    return words


def load_labels(docs, filename):
    with open(filename, 'r') as f:
        for i, line in enumerate(f.readlines()):
            docs[i+1].set_label(int(line.strip()))


def split_by_label(docs):
    split_docs = defaultdict(list)
    for doc_id in docs:
        split_docs[docs[doc_id].label].append(docs[doc_id])

    return split_docs


def probabilities(split_docs, words):
    split = {}
    for label in split_docs:
        split[label] = defaultdict(list)
        length = len(split_docs[label])

        for i, word in enumerate(words):
            word_split = defaultdict(int)
            for doc in split_docs[label]:
                word_split[doc.has_word(i)] += 1
            split[label][i] = (word_split[True] + 1) / float(length + 2)

    return split


def get_label(doc, probs):
    p = defaultdict(int)
    for label in probs:
        p[label] = 1
        for word_id in probs[label]:
            if doc.has_word(word_id):
                p[label] *= probs[label][word_id]
            else:
                p[label] *= (1 - probs[label][word_id])

    max_id = -1
    val = 0
    for i in p:
        if p[i] > val:
            max_id = i
            val = p[i]

    return max_id


def get_training_docs():
    docs = load_data('datasets/trainData.txt')
    load_labels(docs, 'datasets/trainLabel.txt')

    # Split by label
    split_docs = split_by_label(docs)

    return split_docs


def part1():
    docs = get_training_docs()
    words = load_words('datasets/words.txt')

    # Probabilities for each word
    prob = probabilities(docs, words)

    # Classifying testData.txt
    test_docs = load_data('datasets/testData.txt')
    load_labels(test_docs, 'datasets/testLabel.txt')

    split = defaultdict(int)
    for doc_id in test_docs:
        label = get_label(test_docs[doc_id], prob)
        split[label == test_docs[doc_id].label] += 1

    print "Testing accuracy: "
    print "{:10.4f}%".format(split[True] / float(len(test_docs)) * 100)
    print ""

    # Classifying trainData.txt
    test_docs = load_data('datasets/trainData.txt')
    load_labels(test_docs, 'datasets/trainLabel.txt')

    split = defaultdict(int)
    for doc_id in test_docs:
        label = get_label(test_docs[doc_id], prob)
        split[label == test_docs[doc_id].label] += 1

    print "Training accuracy: "
    print "{:10.4f}%".format(split[True] / float(len(test_docs)) * 100)


def discrimanitive_score(prob):
    return math.fabs(math.log(prob[1]) - math.log(prob[2]))


def part2():
    docs = get_training_docs()
    words = load_words('datasets/words.txt')

    pq = queue()
    for i, word in enumerate(words):
        prob = {}
        for label in docs:
            split = defaultdict(int)
            for d in docs[label]:
                split[d.has_word(i)] += 1
            prob[label] = (split[True]+1) / float(len(docs[label]) + 2)
        score = discrimanitive_score(prob)
        pq.put(Score(score, i))

    print ""
    print "Discriminative words: "
    for i in range(0, 10):
        s = pq.get(False)
        print words[s.word_id], s.score


if __name__ == '__main__':
    part1()
    part2()
