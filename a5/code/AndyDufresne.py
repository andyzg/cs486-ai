from pdbot import PDBot

import math
import random

HEURISTICS_ON = False

TAKE_1 = 'take 1'
GIVE_2 = 'give 2'


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


def recent_greediness(prev, curr, steps):
    actions = flat_actions(prev, curr)
    if len(actions) < steps:
        return greed(actions)
    return greed(actions[len(actions)-steps:])


def max_kr_score(count, length, m):
    total = 0
    for i in range(0, count - length):
        total += 1.0 / m ** (count - length - i)
    return total


def kindness_receptiveness(a, b):
    PAST_LENGTH = 5
    RESULT_LENGTH = 2
    MULTIPLIER = 1.05

    total_score = 0
    for i in range(0, len(a) - (PAST_LENGTH+RESULT_LENGTH)):
        im_kind = 1 - greed(a[i:i+PAST_LENGTH])
        theyre_kind = 1 - greed(b[i+PAST_LENGTH:i+PAST_LENGTH+RESULT_LENGTH])
        score = theyre_kind - im_kind
        # score = (1 - past_greed) * -3 + result_greed * 2
        # print 'HEYYYYY', past_greed, result_greed
        # ABSOLUTE:
        # im greedy, they're greedy -> we should keep being greedy ~ 0
        # im greedy, they're nice -> keep being greedy > 0
        # im nice, they're nice -> keep being nice ~ 0
        # im nice, they're not nice -> stop being nice < 0

        # RELATIVE:
        # we're both the same greediness -> try being nicer
        # i'm a bit more greedy -> try being more greedy
        # i'm a lot more greedy -> be less greedy
        # they're a bit more greedy -> be nicer
        # they're a lot more greedy -> be greedy
        # past_greed = 1, result_greed = 1 -> +1
        # past_greed = 0, result_greed = 1 -> +4
        # past_greed = 1, result_greed = 0 -> -4
        # past_greed = 0, result_greed = 0 -> +2

        # weigh recent scores more heavily
        total_score += score / MULTIPLIER ** (len(a) - (PAST_LENGTH+RESULT_LENGTH) - i)

    if total_score == 0:
        return 0.5

    kr_score = max_kr_score(len(a), PAST_LENGTH+RESULT_LENGTH, MULTIPLIER)
    return ((math.fabs(total_score / kr_score) ** (1.0/3)) * (-1 if total_score < 0 else 1) + 1) / 2


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
            return self._their_greed * 1.0 / self.total_steps

        return greed(self.their_current_actions if r == self.current_round else self.their_actions[r])

    def my_greed(self, r=None):
        if self.current_round == 0:
            return 1

        if r is None:
            if self.total_steps - self.steps_per_round[0] == 0:
                return 0.5
            return (self._my_greed - self.steps_per_round[0]) * 1.0 / (self.total_steps - self.steps_per_round[0])

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

    def generous_play(self):
        return random_move({
            TAKE_1: 0.2,
            GIVE_2: 0.8})

    def greedy_play(self):
        return random_move({
            TAKE_1: 0.8,
            GIVE_2: 0.2})

    def my_kindness_receptiveness(self):
        return kindness_receptiveness(flat_actions(self.my_actions, self.my_current_actions),
                                      flat_actions(self.their_actions, self.their_current_actions))

    def their_kindness_receptiveness(self):
        return kindness_receptiveness(flat_actions(self.their_actions, self.their_current_actions),
                                      flat_actions(self.my_actions, self.my_current_actions))

    def get_play(self):
        # We always want to start a turn with a give. Early actions might be
        # weighed more heavily in their algorithms, so we want them to start
        # being more generous to us.
        if self.current_step == 0 and HEURISTICS_ON:
            self.my_last_move = GIVE_2
            return self.my_last_move

        # Start being a lot more greedy near the end because there's less
        # potential for getting the opponent to defect.
        elif self.current_step >= 15 and HEURISTICS_ON:
            self.my_last_move = TAKE_1
            return self.my_last_move

        # We first want to see how the opponent plays if we're generous. The
        # only way we can do well is by leveraging other people's generosity.
        if self.current_round == 0 and HEURISTICS_ON:
            self.my_last_move = self.generous_play()
            return self.my_last_move

        # We want to see how greedy the opponent will be if we are greedy. Will
        # they try to be generous and get us to give them money, or will they be
        # more greedy?
        if (self.current_round == 1 and HEURISTICS_ON):
            self.my_last_move = self.greedy_play()
            return self.my_last_move

        # NON HEURISTIC LOGIC
        # Always start off a bit more generous, and end more greedy

        # 3 properties
        # - Overall greediness, doesn't matter as much
        # - Recent greediness, doesn't matter
        # - How receptive they are to being kind, weigh recent more than old
        greedy_score = 0.1 * self.their_greed() + 0.7 * self.their_recent_greediness(5) + 0.2 * self.their_kindness_receptiveness()
        # print 'Greed score: ', greedy_score

        # print 'How greedy should I be: ', greedy_score
        # print self.their_kindness_receptiveness()
        if random.random() < greedy_score:
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
