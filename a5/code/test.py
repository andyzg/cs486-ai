import random
from pdbot import PDBot

class Test(PDBot):

    def init(self):
        pass

    def get_play(self):
        if random.random() < 0.3:
            return 'take 1'
        return 'give 2'

    def make_play(self, opponent_play):
        pass
