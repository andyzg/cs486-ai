from pdbot import PDBot

from Queue import PriorityQueue as queue
from collections import defaultdict
import math
import random

HEURISTICS_ON = False

TAKE_1 = 'take 1'
GIVE_2 = 'give 2'

###############################
# CALCULATING A DECISION TREE #
###############################
RECENT_GREEDINESS_LENGTH = 4


def debug(*args):
    pass
    # print args


def entropy(entries):
    count = defaultdict(int)
    for e in entries:
        count[e.outcome] += 1

    s = 0.0
    for i in count:
        p = 1.0 * count[i] / len(entries)
        s += -1.0 * p * math.log(p, 2)

    return s


def information_gain(entries, index, value):
    smaller = []
    bigger = []
    for e in entries:
        if e[index] < value:
            smaller.append(e)
        else:
            bigger.append(e)

    score = entropy(entries) \
        - 1.0 * len(smaller) / len(entries) * entropy(smaller) \
        - 1.0 * len(bigger) / len(entries) * entropy(bigger)

    return score


def find_optimal_split(entries, index):
    minimum = 100
    maximum = 0
    for i in entries:
        minimum = min(i[index], minimum)
        maximum = max(i[index], maximum)

    max_info_gain = 0
    split = -1
    for i in range(int(minimum), int(maximum)-1):
        ig = information_gain(entries, index, i + 0.5)
        if ig > max_info_gain:
            max_info_gain = ig
            split = i + 0.5

    return split


class Node:

    def __init__(self, entries, indices, index, value):
        self.entries = entries
        self.indices = indices
        self.children = {}
        self.split = value
        self.index = index

        self.less = []
        self.more = []
        for e in entries:
            if e[index] < value:
                self.less.append(e)
            else:
                self.more.append(e)

    def add_child(self, val, node):
        self.children[val] = node

    def has_child(self, val):
        return val in self.children

    def is_end(self):
        return len(self.entries) == 0 or len(self.indices) == len(self.entries[0])

    def predict(self, entries):
        take_count = 0
        for i in entries:
            if i.outcome == TAKE_1:
                take_count += 1
        return take_count * 1.0 / len(entries)

    def predict_outcome(self, values):
        if values[self.index] < self.split:
            if False in self.children:
                return self.children[False].predict_outcome(values)
            else:
                return self.predict(self.less)
        else:
            if True in self.children:
                return self.children[True].predict_outcome(values)
            else:
                return self.predict(self.more)


class Option:

    def __init__(self, n1, n2, index, split, on_right):
        self.n1 = n1
        self.n2 = n2
        self.index = index
        self.on_right = on_right
        self.split = split
        self.gain = information_gain(self.n2.entries, self.index, split)

    def __cmp__(self, option):
        if self.gain < option.gain:
            return 1
        elif self.gain > option.gain:
            return -1
        return 0


class Entry:

    def __init__(self, rs, mrg, trg, overall_g, outcome):
        self.relative_score = rs
        self.my_recent_greed = int(round(mrg * RECENT_GREEDINESS_LENGTH))
        self.their_recent_greed = int(round(trg * RECENT_GREEDINESS_LENGTH))
        self.my_overall_greed = int(round(overall_g * RECENT_GREEDINESS_LENGTH))
        self.arr = [self.relative_score,
                    self.my_recent_greed,
                    self.their_recent_greed,
                    self.my_overall_greed]
        self.outcome = outcome

    def __len__(self):
        return len(self.arr)

    def __getitem__(self, i):
        return self.arr[i]

    def __iter__(self):
        for i in self.arr:
            yield i


def get_entry(m, t, step):
    me = m[0:step-1]
    them = t[0:step-1]

    if my_score(me, them) == 0:
        print 'wait what', me, them
    relative_score = round((their_score(me, them) * 1.0 + 1) / (my_score(me, them) + 1) * 10)
    my_recent_greed = recent_greediness(me, RECENT_GREEDINESS_LENGTH)
    my_overall_greed = greed(me)
    their_recent_greed = recent_greediness(them, RECENT_GREEDINESS_LENGTH)
    outcome = t[step-1]
    return Entry(relative_score,
                 my_recent_greed,
                 their_recent_greed,
                 my_overall_greed,
                 outcome)


def get_options(node):
    f_count = 4
    options = []

    # Populate the priorty queue with options
    for i in range(0, f_count):
        if i in node.indices:
            continue
        # Process left side
        if len(node.less) > 0:
            less_split = find_optimal_split(node.less, i)
            less_n = Node(node.less, node.indices + [i], i, less_split)
            options.append(Option(node, less_n, i, less_split, False))

        if len(node.more) > 0:
            more_split = find_optimal_split(node.more, i)
            more_n = Node(node.more, node.indices + [i], i, more_split)
            options.append(Option(node, more_n, i, more_split, True))

    return options


def predict_next_move(me, them):
    if len(me) < 10:
        return 0.5  # We need some existing data

    # We can build a Bayesian Network using Naive Bayes to calculate each CPT
    # Features:
    # - Relative score <- Assume they want to beat us
    # - My recent greed <- Assume recent greed has a heavy impact
    # - My overall greed <- Assume overall greed also has some impact
    # - Their recent greed <- Assume they'll try to compensate
    entries = []
    for i in range(5, len(me)):
        entries.append(get_entry(me, them, i))

    f_count = len(entries[0])  # Feature count

    # Get the root node
    index = -1
    info_gain = 0
    max_split = None
    for i in range(0, f_count):
        split = find_optimal_split(entries, i)
        ig = information_gain(entries, i, split)
        if ig > info_gain:
            info_gain = ig
            max_split
            index = i

    pq = queue()
    root = Node(entries, [index], index, max_split)
    node_count = 1

    options = get_options(root)
    for o in options:
        pq.put(o)

    while node_count <= 3:
        o = pq.get()
        if o.n1.has_child(o.on_right):
            continue
        parent_node = o.n1
        node = o.n2
        parent_node.add_child(o.on_right, node)

        options = get_options(node)
        for o in options:
            pq.put(o)

        node_count += 1

    relative_score = round(their_score(me, them) * 1.0 / my_score(me, them) * 10)
    my_recent_greed = recent_greediness(me, RECENT_GREEDINESS_LENGTH)
    their_recent_greed = recent_greediness(them, RECENT_GREEDINESS_LENGTH)
    my_overall_greed = greed(me)

    return root.predict_outcome([relative_score, my_recent_greed, their_recent_greed, my_overall_greed])


###############################
# END OF CALCULATION, NOW AI  #
###############################

def random_move(options):
    odds = random.random() * (options[TAKE_1] + options[GIVE_2])
    if odds < options[TAKE_1]:
        return TAKE_1
    return GIVE_2


def flat_actions(l, a=[]):
    flat_list = []
    for i in l:
        for j in i:
            flat_list.append(j)
    for i in a:
        flat_list.append(i)
    return flat_list


def greed(a):
    if len(a) == 0:
        return 0.5
    counts = {i: a.count(i) for i in a}
    return counts.get(TAKE_1, 0) * 1.0 / (counts.get(TAKE_1, 0) + counts.get(GIVE_2, 0))


def my_score(me, them):
    score = 0
    for i in me:
        if i == TAKE_1:
            score += 1
    for i in them:
        if i == GIVE_2:
            score += 2
    return score


def their_score(me, them):
    return my_score(them, me)


def recent_greediness(actions, steps):
    if len(actions) < steps:
        return greed(actions)
    return greed(actions[len(actions)-steps:])


def kindness_receptiveness(a, b):
    # ABSOLUTE:
    # im greedy, they're greedy -> we should keep being greedy ~ 0
    # im greedy, they're nice -> keep being greedy > 0
    # im nice, they're nice -> keep being nice ~ 0
    # im nice, they're not nice -> stop being nice < 0

    # RELATIVE:
    # we're both the same greediness -> randomly move around
    # i'm a bit more greedy -> try being more greedy
    # i'm a lot more greedy -> be less greedy
    # they're a bit more greedy -> be nicer
    # they're a lot more greedy -> be greedy
    LENGTH = 7  # Arbitrary
    mrg = recent_greediness(a, LENGTH)  # my recent greediness
    trg = recent_greediness(a, LENGTH)  # their recent greediness

    greed_diff = mrg - trg
    if math.fabs(greed_diff) < 0.05:
        # Be a bit greedier
        return min(min(trg, mrg) + (random.random() - 0.7) * 0.2, 1)

    if greed_diff >= 0.05 and greed_diff < 0.15:
        # Be a bit more greedy
        return min(1, trg)

    if greed_diff > 0.15:
        # Be less greedy, but still be somewhat greedy
        return min(1, trg + 0.1)

    if greed_diff > -0.15 and greed_diff <= 0.05:
        # Be a bit nicer
        return max(0, mrg - 0.05)

    if greed_diff <= -0.15:
        # Getting taken advantage of, be more greedy
        return min(1, mrg + 0.1)

    # Default
    return 0.5


class AndyDufresne(PDBot):

    def __init__(self):
        # GLOBAL VARIABLES
        # Depending on the opponent's opening, we can gauge if their strategy is
        # greedy or not. We calculate this based on the number of times they
        # take vs when they give
        self._their_greed = 0
        self._my_greed = 0
        self.total_steps = 0

        self.their_moves = []
        self.my_moves = []

        self.my_scores = []
        self.their_score = []

        self.my_actions = []
        self.their_actions = []

        self.steps_per_round = []

        # CURRENT VARIABLES
        self.current_round = -1
        self.current_step = 0

        self.my_current_score = 0
        self.their_current_score = 0

        self.my_current_actions = []
        self.their_current_actions = []

    def my_flat_actions(self):
        return flat_actions(self.my_actions, self.my_current_actions)

    def their_flat_actions(self):
        return flat_actions(self.their_actions, self.their_current_actions)

    def their_greed(self, r=None):
        if r is None:
            if self.total_steps == 0:
                return 0.5  # Assume 0.5 start
            return greed(flat_actions(self.their_actions, self.their_current_actions))

        return greed(self.their_current_actions if r == self.current_round else self.their_actions[r])

    def my_greed(self, r=None):
        if r is None:
            if self.total_steps == 0:
                return 0.5
            return greed(flat_actions(self.my_actions, self.my_current_actions))

        return greed(self.my_current_actions if r == self.current_round else self.my_actions[r])

    def my_recent_greediness(self, steps):
        return recent_greediness(flat_actions(self.my_actions, self.my_current_actions), steps)

    def their_recent_greediness(self, steps):
        return recent_greediness(flat_actions(self.their_actions, self.their_current_actions), steps)

    def init(self):
        # If this isn't the first round
        if self.current_step > 0:
            self.steps_per_round.append(self.current_step)

            self.my_actions.append(self.my_current_actions)
            self.their_actions.append(self.their_current_actions)

            self.my_current_actions = []
            self.their_current_actions = []

        self.my_score = 0
        self.opp_score = 0

        self.my_last_move = None
        self.their_last_move = None
        self.current_round += 1
        # A round consists of 15+-3 steps
        self.current_step = 0

    def kr_score(self):
        return kindness_receptiveness(flat_actions(self.their_actions, self.their_current_actions),
                                      flat_actions(self.my_actions, self.my_current_actions))

    def get_play(self):
        # Always start off a bit more generous, and end more greedy
        their_greed = self.their_greed()
        their_recent_greed = self.their_recent_greediness(5)
        kr_score = self.kr_score()
        predicted_move = predict_next_move(flat_actions(self.my_actions, self.my_current_actions),
                                           flat_actions(self.their_actions, self.their_current_actions))
        greed_score = 0.5
        if self.my_recent_greediness(5) > 0.7 and random.random() < 0.5:
            # I've been too greedy, start being more generous
            debug('Im too greedy recently')
            greed_score = random.random() * 0.2

        elif self.my_greed() > 0.7 and random.random() < 0.5:
            # I've been too greedy, start being more generous
            debug('Im too greedy', self.my_greed())
            greed_score = random.random() * 0.3

        elif self.my_current_score + 9 < self.their_current_score:
            # Don't want them to get ahead by more than 5
            greed_score = their_greed*0.1 + their_recent_greed*0.6 + kr_score*0.3
            debug('DONT LET THEM GET AHEAD')

        else:
            if predicted_move < 0.4:
                # they're likely to give, give back
                greed_score = their_greed*0.1 + their_recent_greed*0.2 + kr_score*0.2 + (1-predicted_move)*0.5
                debug('Theylll probably give back')
            elif predicted_move > 0.6:
                # they're likely to take, we should take
                greed_score = their_greed*0.1 + their_recent_greed*0.2 + kr_score*0.2 + predicted_move*0.5
                debug('Theyll probably take')
            else:
                # Neutral gameplay
                greed_score = their_greed*0.1 + their_recent_greed*0.4 + kr_score*0.5
                debug('NEUTRAL!')

        if random.random() < greed_score:
            self.my_last_move = TAKE_1
        else:
            self.my_last_move = GIVE_2

        return self.my_last_move

    def make_play(self, opponent_play):
        self.current_step += 1
        self.total_steps += 1
        self.their_last_move = opponent_play

        # Score calculation from their action
        if opponent_play == GIVE_2:
            self.my_current_score += 2
        else:
            self.their_current_score += 1
            self._their_greed += 1

        # Score calculation from my action
        if self.my_last_move == GIVE_2:
            self.their_current_score += 2
        else:
            self.my_current_score += 1
            self._my_greed += 1

        self.my_current_actions.append(self.my_last_move)
        self.their_current_actions.append(self.their_last_move)
