#import the base class
from pdbot import PDBot

#add whatever libraries you need here from the standard library set
import random

class AwesomeBot(PDBot):
    #can add a constructor to set up any state you need
    def __init__(self):
        #initialise
        #tit-for-tat always starts with cooperation
        self.other_last_play="give 2"


    def init(self):
        self.other_last_play="give 2"
    #get_play is a function that takes no arguments
    #and returns one of the two strings "give 2" or "take 1" 
    #denoting the next play your agent will take in the game
    def get_play(self):
        #tit-for-tat always returns the other's last play
        #return self.other_last_play
        #almost-tit-for-tat
        if random.random() < 0.9:
            myplay = self.other_last_play
        else:
            if random.random() > 0.5:
                myplay =  "give 2"
            else:
                myplay =  "take 1"
        #you may also want to store myplay here, although awesomebot doesn't need this
        self.my_last_play = myplay

        return myplay

    #make_play is a function that takes a single string argument
    #that is either "give 2" or "take 1" denoting the opponent's
    #last play in the game    
    def make_play(self,opponent_play):
        #store for next round
        self.other_last_play = opponent_play
        return
        
if __name__ == "__main__":
    

    pd_agent = AwesomeBot()

    done = False
    iteration = 1
    agent_score = 0
    client_score = 0
    pd_agent.init()
    while not done:
        print 100*"*"
        print "game "+str(iteration)+": pd-bot is thinking ..."
        agent_action = pd_agent.get_play()

        client_action = raw_input("your action (give 2 or take 1, anything else stops play): ")

        print "pd-bot's action is to: ",agent_action

        

        if client_action == "give 2" or client_action == "take 1":
            pd_agent.make_play(client_action)
        else:
            done = True

        if client_action == "give 2":
            agent_score += 2
        if agent_action == "give 2":
            client_score += 2
        if agent_action == "take 1":
            agent_score += 1
        if client_action == "take 1":
            client_score += 1

        print "your score:    ",client_score," -:",client_score*"*"
        print "pd-bots score: ",agent_score," -:",agent_score*"*"
        
        iteration += 1
