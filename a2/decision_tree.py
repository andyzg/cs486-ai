from collections import defaultdict
from Queue import PriorityQueue as queue
import math
import sys


class Node:

    def __init__(self, word_id, entropy, docs, word_ids):
        self.word_id = word_id
        self.entropy = entropy
        self.children = {}
        self.docs = docs
        self.word_ids = word_ids

    def add_child(self, node, val):
        self.children[val] = node

    def has_child(self, val):
        return val in self.children

    def get_split(self):
        labels = defaultdict(int)
        for d in self.docs:
            labels[d.label] += 1
        return labels

    def __cmp__(self, node):
        if self.entropy < node.entropy:
            return -1
        elif self.entropy > node.entropy:
            return 1
        return 0

    def __str__(self):
        return str(self.word_id) + ' ' + str(self.entropy) + ' ' + 'docs: ' + str(len(self.docs)) + ' ' + 'word_ids: ' + str(self.word_ids)


class Option:

    def __init__(self, n1, n2, word_id, contains):
        self.n1 = n1
        self.n2 = n2
        self.gain = information_gain(n2.docs, n2.word_id)
        self.contains = contains

    def __cmp__(self, option):
        if self.gain < option.gain:
            return 1
        elif self.gain > option.gain:
            return -1
        return 0

    def __str__(self):
        return str(self.n1.word_id) + ' ' + str(self.n2.word_id) + ' ' + str(self.gain) + ' ' + str(self.contains)


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


def print_tree(node):
    if False in node.children:
        print_tree(node.children[False])

    print(node.word_id, node.children, node.entropy, node.get_split())

    if True in node.children:
        print_tree(node.children[True])


def main():
    docs = load_data('trainData.txt')
    docs = [docs[i] for i in docs]
    load_labels(docs, 'trainLabel.txt')
    words = load_words('words.txt')
    pq = queue()

    nodes = []

    root = Node(None, entropy(docs), docs, [])
    for i in range(1, len(words)+1):
        n = Node(i, entropy(docs), docs, [i])
        pq.put(Option(root, n, n.word_id, True))

    start = pq.get()
    while not pq.empty():
        try:
            x = pq.get(False)
            print(str(x), x.n2.get_split())
        except:
            continue
        pq.task_done()

    pq.put(start)
    nodes.append(n)
    node_count = 1

    while node_count < 10:
        o = pq.get()
        parent_parent_node = o.n1
        parent_node = o.n2
        if parent_parent_node.has_child(o.contains):
            continue

        print(str(parent_node))
        print(str(o))
        parent_parent_node.add_child(parent_node, o.contains)

        has_word = []
        missing_word = []
        print('Parent node word id', parent_node.word_id)
        for d in parent_node.docs:
            if d.has_word(parent_node.word_id):
                has_word.append(d)
            else:
                missing_word.append(d)

        print('has word', len(has_word))
        print('missing word', len(missing_word))
        for word in range(1, len(words)+1):
            if word not in parent_node.word_ids:
                pq.put(Option(parent_node, Node(word, entropy(has_word), has_word, parent_node.word_ids + [word]), word, True))
                pq.put(Option(parent_node, Node(word, entropy(missing_word), missing_word, parent_node.word_ids + [word]), word, False))

        node_count += 1
        print('')

    print_tree(root)

    return 0


if __name__ == '__main__':
    sys.exit(main())
