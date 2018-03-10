from collections import defaultdict


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


def main():
    docs = load_data('datasets/trainData.txt')
    load_labels(docs, 'datasets/trainLabel.txt')
    words = load_words('datasets/words.txt')

    # Split by label
    split_docs = split_by_label(docs)

    # Probabilities for each word
    prob = probabilities(split_docs, words)

    test_docs = load_data('datasets/testData.txt')
    load_labels(test_docs, 'datasets/testLabel.txt')
    split = defaultdict(int)
    for doc_id in test_docs:
        label = get_label(test_docs[doc_id], prob)
        print label == test_docs[doc_id].label
        split[label == test_docs[doc_id].label] += 1

    print split

if __name__ == '__main__':
    main()
