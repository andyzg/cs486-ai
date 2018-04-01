###############################################################
# ABSTRACT BASE CLASS FOR PDBOTS
# A PDBot has two methods:
# get_play is called to get the bots next play
# make_play is called to tell teh bot what the opponent played
###############################################################
from abc import ABCMeta, abstractmethod

class PDBot:
    __metaclass__=ABCMeta
    
    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def get_play(self):
        pass

    @abstractmethod
    def make_play(self, opponent_play):
        pass



