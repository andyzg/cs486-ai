from AwesomeBot import AwesomeBot
from AndyDufresne import AndyDufresne
from test import Test
import sys

pd_agent = Test()
me = AndyDufresne()

def main():
    done = False

    my_scores = []
    pd_scores = []

    for i in range(0, 10):
        iteration = 1
        agent_score = 0
        client_score = 0
        pd_agent.init()
        me.init()

        for j in range(0, 15):
            agent_action = pd_agent.get_play()
            my_action = me.get_play()

            pd_agent.make_play(my_action)
            me.make_play(agent_action)
            print 'Actions: agent', agent_action, ', I', my_action

            if my_action == "give 2":
                agent_score += 2
            elif my_action == "take 1":
                client_score += 1

            if agent_action == "give 2":
                client_score += 2
            elif agent_action == "take 1":
                agent_score += 1

        print "your score:    ",client_score," -:",client_score*"*"
        print "pd-bots score: ",agent_score," -:",agent_score*"*"
        my_scores.append(client_score)
        pd_scores.append(agent_score)

    print 'My mean score: ', sum(my_scores) * 1.0 / len(my_scores)
    print 'PD mean score: ', sum(pd_scores) * 1.0 / len(pd_scores)


def interact():
    pd_agent = AndyDufresne()

    done = False
    iteration = 1
    agent_score = 0
    client_score = 0
    for j in range(0, 2):
        pd_agent.init()
        for i in range(0, 15):
            agent_action = pd_agent.get_play()

            client_action = raw_input("")


            print "pd-bot's action is to: ",agent_action

            if client_action == "give 2" or client_action == '2':
                agent_score += 2
                pd_agent.make_play('give 2')
            if agent_action == "give 2":
                client_score += 2
            if agent_action == "take 1":
                agent_score += 1
            if client_action == "take 1" or client_action == '1':
                client_score += 1
                pd_agent.make_play('take 1')

            print "your score:    ",client_score," -:",client_score*"*"
            print "pd-bots score: ",agent_score," -:",agent_score*"*"

if __name__ == '__main__':
    if len(sys.argv) > 1:
        interact()
    else:
        main()
