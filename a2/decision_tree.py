from collections import defaultdict
from Queue import PriorityQueue as queue
import math
import sys


class Node:

    def __init__(self, word_id, gain, docs):
        self.word_id = word_id
        self.gain = gain
        self.children = {}
        self.docs = docs

    def add_child(self, node, val):
        self.children[val] = node

    def __cmp__(self, node):
        if self.gain < node.gain:
            return -1
        elif self.gain > node.gain:
            return 1
        return 0


class Option:

    def __init__(self, n1, n2):
        self.n1 = n1
        self.n2 = n2
        self.gain = information_gain(n1.docs, n2.word_id)

    def __cmp__(self, option):
        if self.gain < option.gain:
            return -1
        elif self.gain > option.gain:
            return 1
        return 0


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


def entropy(docs):
    count = defaultdict(int)
    for doc in docs:
        count[doc.label] += 1

    s = 0.0
    for i in count:
        p = 1.0 * count[i] / len(docs)
        s += -1.0 * p * math.log(p, 2)

    return s


def information_gain(docs, word_id, approach=1):
    has_word = []
    missing_word = []
    for doc in docs:
        if doc.has_word(word_id):
            has_word.append(doc)
        else:
            missing_word.append(doc)

    has_word_entropy = entropy(has_word)
    missing_word_entropy = entropy(missing_word)

    if approach == 2:
        return entropy(docs) - \
            (1.0 * len(has_word) / len(docs) * has_word_entropy +
             1.0 * len(missing_word) / len(docs) * missing_word_entropy)

    return entropy(docs) - (0.5 * has_word_entropy + 0.5 * missing_word_entropy)


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

            docs[doc_id].add_word(word_id)
            last_index = doc_id

    return docs


def load_labels(docs, filename):
    with open(filename, 'r') as f:
        for i, line in enumerate(f.readlines()):
            docs[i].set_label(int(line.strip()))


def load_words(filename):
    words = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            words.append(line.strip())

    return words


def main():
    docs = load_data('trainData.txt')
    docs = [docs[i] for i in docs]
    load_labels(docs, 'trainLabel.txt')
    words = load_words('words.txt')
    pq = queue()

    node_count = 0
    nodes = []

    for i in range(0, len(words)):
        pq.put(Node(information_gain(docs, i), i, docs))

    n = pq.get()
    nodes.append(n)

    while node_count < 100:
        pass
    print(pq)

    return 0


if __name__ == '__main__':
    sys.exit(main())
